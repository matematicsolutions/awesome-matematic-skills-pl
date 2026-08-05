/**
 * M1: co dokladnie zmienia sie w docProps/core.xml przy zapisie i czy da sie to wylaczyc.
 * M2: polski fixture (naglowki + numeracja + PRZYPISY DOLNE) - round-trip.
 *
 * RODO: M1 wypisuje wylacznie NAZWY tagow XML z docProps (metadane pakietu, nie tresc pisma).
 */
import JSZip from 'jszip'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { parseDocx, saveDocx, type SaveBlock } from '../src/index'
import { patchParagraphTexts } from '../src/text-patch'
import { buildDocx } from '../tests/helpers/build-docx'

const sha = (b: Uint8Array) => createHash('sha256').update(b).digest('hex').slice(0, 16)

async function part(bytes: Uint8Array, name: string): Promise<string | null> {
  const f = (await JSZip.loadAsync(bytes)).file(name)
  return f ? f.async('string') : null
}
async function partBytes(bytes: Uint8Array, name: string): Promise<Uint8Array | null> {
  const f = (await JSZip.loadAsync(bytes)).file(name)
  return f ? f.async('uint8array') : null
}

/** nazwy tagow + czy wartosc sie zmienila - BEZ wypisywania wartosci poza timestampami */
function tagDelta(a: string, b: string): string[] {
  const grab = (s: string) => {
    const m = new Map<string, string>()
    const re = /<([a-zA-Z0-9:]+)(?:\s[^>]*)?>([^<]*)<\/\1>/g
    let x: RegExpExecArray | null
    while ((x = re.exec(s)) !== null) m.set(x[1], x[2])
    return m
  }
  const ma = grab(a)
  const mb = grab(b)
  const keys = new Set([...ma.keys(), ...mb.keys()])
  const out: string[] = []
  for (const k of keys) {
    const va = ma.get(k)
    const vb = mb.get(k)
    if (va !== vb) {
      const isTime = /modified|created|dcterms/i.test(k)
      out.push(isTime ? `${k}: ${va ?? '(brak)'} -> ${vb ?? '(brak)'}` : `${k}: <zmiana wartosci>`)
    }
  }
  return out
}

const textOf = (x: string) => {
  const re = /<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g
  let m: RegExpExecArray | null
  let s = ''
  while ((m = re.exec(x)) !== null) s += m[1]
  return s
}

// ---------------------------------------------------------------- M1
console.log('=== M1: docProps/core.xml - co sie zmienia i czy savedAt to gasi ===')
for (const f of process.argv.slice(2)) {
  const input = new Uint8Array(await readFile(f))
  const doc = await parseDocx(input)
  const visible = doc.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
  const blocks: SaveBlock[] = visible.map((b) => ({
    kind: 'original',
    docxIndex: b.docxIndex as number,
  }))
  const coreIn = await part(input, 'docProps/core.xml')
  if (coreIn === null) {
    console.log(`${basename(f)}\tBRAK docProps/core.xml -> nie ma czego zmieniac`)
    continue
  }
  // wymus realny zapis (no-op zwraca oryginal skrotem), edytujac 1 akapit
  const target = visible.find((b) => b.originalXml && textOf(b.originalXml).trim().length > 3)
  if (!target) continue
  const patched = patchParagraphTexts(target.originalXml as string, textOf(target.originalXml as string) + ' X')
  if (patched === null) continue
  const edited: SaveBlock[] = visible.map((b) =>
    b.docxIndex === target.docxIndex
      ? { kind: 'xml', xml: patched, docxIndex: b.docxIndex as number }
      : { kind: 'original', docxIndex: b.docxIndex as number },
  )

  const def = await saveDocx(doc, edited)
  const coreDef = (await part(def, 'docProps/core.xml')) as string
  const delta = tagDelta(coreIn, coreDef)

  // proba: podac savedAt rowny oryginalnemu dcterms:modified
  const origMod = /<dcterms:modified[^>]*>([^<]*)<\/dcterms:modified>/.exec(coreIn)?.[1]
  let pinned = 'n/d'
  if (origMod) {
    const p = await saveDocx(doc, edited, { savedAt: origMod })
    const coreP = (await part(p, 'docProps/core.xml')) as string
    pinned = coreP === coreIn ? 'IDENTYCZNY' : `nadal rozny: ${tagDelta(coreIn, coreP).join('; ')}`
  }
  console.log(`${basename(f)}\tdomyslnie: ${delta.join('; ') || '(brak roznic)'}\t| savedAt=orig: ${pinned}`)
  void blocks
}

// ---------------------------------------------------------------- M2
console.log('')
console.log('=== M2: polski fixture - naglowki + numeracja + PRZYPISY DOLNE ===')

const FOOTNOTES_XML =
  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' +
  '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">' +
  '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>' +
  '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>' +
  '<w:footnote w:id="1"><w:p><w:r><w:footnoteRef/></w:r><w:r><w:t xml:space="preserve"> ' +
  'Wyrok SN z 12 marca 2019 r., II CSK 345/18, OSNC 2020, nr 1, poz. 7.</w:t></w:r></w:p></w:footnote>' +
  '<w:footnote w:id="2"><w:p><w:r><w:footnoteRef/></w:r><w:r><w:rPr><w:i/></w:rPr>' +
  '<w:t xml:space="preserve"> Zob. art. 385¹ § 1 k.c. oraz art. 58 § 2 k.c.</w:t></w:r></w:p></w:footnote>' +
  '</w:footnotes>'

const BODY =
  '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>I. Stan faktyczny sprawy</w:t></w:r></w:p>' +
  '<w:p><w:r><w:t xml:space="preserve">Pozwana spółka zawarła z powodem umowę o świadczenie usług</w:t></w:r>' +
  '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="1"/></w:r>' +
  '<w:r><w:t xml:space="preserve">, której § 7 zastrzegał karę umowną.</w:t></w:r></w:p>' +
  '<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:r><w:t>1.1. Zarzuty apelacji</w:t></w:r></w:p>' +
  '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr></w:pPr>' +
  '<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">Naruszenie prawa materialnego </w:t></w:r>' +
  '<w:r><w:t>przez błędną wykładnię art. 483 § 1 k.c.</w:t></w:r>' +
  '<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="2"/></w:r></w:p>' +
  '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr></w:pPr>' +
  '<w:r><w:t>Naruszenie przepisów postępowania, tj. art. 233 § 1 k.p.c.</w:t></w:r></w:p>' +
  '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr>' +
  '<w:r><w:t>Wniosek o zmianę zaskarżonego wyroku w całości.</w:t></w:r></w:p>'

const fixture = await buildDocx({
  bodyXml: BODY,
  withNumbering: true,
  extraStylesXml:
    '<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/>' +
    '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>',
  extraRels:
    '<Relationship Id="rId20" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>',
  extraParts: [
    {
      path: 'word/footnotes.xml',
      xml: FOOTNOTES_XML,
      contentType:
        'application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml',
    },
  ],
})

const fdoc = await parseDocx(fixture)
const fvis = fdoc.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
console.log(`bloki widoczne: ${fvis.length}`)
console.log(`typy blokow: ${fvis.map((b) => b.type).join(', ')}`)
console.log(`przypisy sparsowane: ${fdoc.footnotes.length}`)
console.log(
  `numeracja na blokach: ${fvis.filter((b) => b.list).map((b) => `${b.list!.kind}/numId=${b.list!.numId}`).join(', ')}`,
)

// no-op
const noop = await saveDocx(
  fdoc,
  fvis.map((b) => ({ kind: 'original', docxIndex: b.docxIndex as number })),
)
console.log(
  `no-op bajt-w-bajt: ${Buffer.compare(Buffer.from(noop), Buffer.from(fixture)) === 0 ? 'OK' : 'ROZNI SIE'}`,
)

// edycja akapitu numerowanego, ktory NIESIE przypis
const tgt = fvis.find((b) => b.list && (b.originalXml ?? '').includes('footnoteReference'))
if (!tgt) {
  console.log('BRAK akapitu numerowanego z przypisem - fixture do poprawy')
} else {
  const oxml = tgt.originalXml as string
  const np = patchParagraphTexts(oxml, textOf(oxml) + ' (zmiana redakcyjna)')
  if (np === null) {
    console.log('patchParagraphTexts zwrocil null')
  } else {
    const saved = await saveDocx(
      fdoc,
      fvis.map((b) =>
        b.docxIndex === tgt.docxIndex
          ? ({ kind: 'xml', xml: np, docxIndex: b.docxIndex as number } as SaveBlock)
          : ({ kind: 'original', docxIndex: b.docxIndex as number } as SaveBlock),
      ),
    )
    const zin = await JSZip.loadAsync(fixture)
    const zout = await JSZip.loadAsync(saved)
    const changed: string[] = []
    for (const name of Object.keys(zin.files)) {
      if (zin.files[name].dir) continue
      const a = await partBytes(fixture, name)
      const b = await partBytes(saved, name)
      if (!b || sha(a!) !== sha(b)) changed.push(name)
    }
    console.log(`zmienione wpisy ZIP: ${changed.join(', ') || '(zadne)'}`)
    console.log(
      `footnotes.xml nietkniety: ${
        sha((await partBytes(fixture, 'word/footnotes.xml'))!) ===
        sha((await partBytes(saved, 'word/footnotes.xml'))!)
          ? 'OK'
          : 'ZMIENIONY'
      }`,
    )
    console.log(
      `numbering.xml nietkniety: ${
        sha((await partBytes(fixture, 'word/numbering.xml'))!) ===
        sha((await partBytes(saved, 'word/numbering.xml'))!)
          ? 'OK'
          : 'ZMIENIONY'
      }`,
    )
    console.log(
      `styles.xml nietkniety: ${
        sha((await partBytes(fixture, 'word/styles.xml'))!) ===
        sha((await partBytes(saved, 'word/styles.xml'))!)
          ? 'OK'
          : 'ZMIENIONY'
      }`,
    )
    const ndx = (await part(saved, 'word/document.xml')) as string
    const others = fvis.filter((b) => b.docxIndex !== tgt.docxIndex && b.originalXml)
    const kept = others.filter((b) => ndx.includes(b.originalXml as string)).length
    console.log(`inne akapity bajt-identyczne: ${kept}/${others.length}`)
    console.log(
      `w:pPr (styl+numeracja) edytowanego: ${
        /<w:pPr>[\s\S]*?<\/w:pPr>/.exec(oxml)?.[0] === /<w:pPr>[\s\S]*?<\/w:pPr>/.exec(np)?.[0]
          ? 'OK'
          : 'ZMIENIONY'
      }`,
    )
    console.log(
      `odwolanie do przypisu w akapicie zachowane: ${np.includes('<w:footnoteReference w:id="2"/>') ? 'OK' : 'UTRACONE'}`,
    )
    console.log(`pogrubiony run (w:b) zachowany: ${np.includes('<w:b/>') ? 'OK' : 'UTRACONY'}`)
    const re = await parseDocx(saved)
    const reVis = re.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    const reT = reVis.find((b) => b.docxIndex === tgt.docxIndex)
    console.log(
      `reparse: bloki ${reVis.length}/${fvis.length}, przypisy ${re.footnotes.length}/${fdoc.footnotes.length}, ` +
        `lista ${JSON.stringify(reT?.list)} (bylo ${JSON.stringify(tgt.list)})`,
    )
  }
}
