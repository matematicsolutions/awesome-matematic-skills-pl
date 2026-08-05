/**
 * Bulk round-trip fidelity harness dla @genoffice/docx-engine na PRAWDZIWYCH plikach .docx.
 *
 * RODO / tajemnica adwokacka: skrypt NIE wypisuje ani jednego znaku tresci dokumentu.
 * Raportuje wylacznie metryki strukturalne (nazwy wpisow ZIP, liczniki, verdicty).
 *
 * Scenariusze na kazdym pliku:
 *   A. no-op       - parse -> save bez zmian  -> czy wyjscie jest bajt w bajt rowne wejsciu
 *   B. 1 akapit    - chirurgiczna podmiana tekstu JEDNEGO akapitu (preferowany numerowany)
 *                    -> ktore wpisy ZIP sie zmienily
 *                    -> ile pozostalych akapitow zachowalo dokladny oryginalny XML
 *                    -> czy w:pPr edytowanego akapitu (styl + numeracja) przetrwal co do bajtu
 *                    -> czy w:rPr (formatowanie runow) przetrwaly
 *                    -> czy plik po zapisie nadal sie parsuje i ma te sama liczbe blokow
 */
import JSZip from 'jszip'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { parseDocx, saveDocx, type SaveBlock } from '../src/index'
import { patchParagraphTexts } from '../src/text-patch'

const SUFFIX = ' [ZMIANA TESTOWA ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ]'

function sha(b: Uint8Array): string {
  return createHash('sha256').update(b).digest('hex').slice(0, 16)
}

async function entryHashes(bytes: Uint8Array): Promise<Map<string, string>> {
  const zip = await JSZip.loadAsync(bytes)
  const out = new Map<string, string>()
  for (const [name, entry] of Object.entries(zip.files)) {
    if (!entry.dir) out.set(name, sha(await entry.async('uint8array')))
  }
  return out
}

function textOf(paraXml: string): string {
  const re = /<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g
  let m: RegExpExecArray | null
  let s = ''
  while ((m = re.exec(paraXml)) !== null) {
    s += m[1]
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&apos;/g, "'")
      .replace(/&amp;/g, '&')
  }
  return s
}

function firstPPr(paraXml: string): string | null {
  const m = /<w:pPr>[\s\S]*?<\/w:pPr>/.exec(paraXml)
  return m ? m[0] : null
}

function allRPr(paraXml: string): string[] {
  return paraXml.match(/<w:rPr>[\s\S]*?<\/w:rPr>/g) ?? []
}

interface Row {
  file: string
  blocks: number | string
  noop: string
  zipDelta: string
  paraKept: string
  pPr: string
  rPr: string
  reparse: string
  note: string
}

const rows: Row[] = []

for (const f of process.argv.slice(2)) {
  const name = basename(f)
  const row: Row = {
    file: name,
    blocks: '-',
    noop: '-',
    zipDelta: '-',
    paraKept: '-',
    pPr: '-',
    rPr: '-',
    reparse: '-',
    note: '',
  }
  try {
    const input = new Uint8Array(await readFile(f))
    const doc = await parseDocx(input)
    const visible = doc.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    row.blocks = visible.length

    // --- A. no-op ---
    const asOriginal: SaveBlock[] = visible.map((b) => ({
      kind: 'original',
      docxIndex: b.docxIndex as number,
    }))
    const noop = await saveDocx(doc, asOriginal)
    row.noop =
      noop.length === input.length && Buffer.compare(Buffer.from(noop), Buffer.from(input)) === 0
        ? 'OK'
        : 'ROZNI SIE'

    // --- B. wybor celu: najchetniej akapit numerowany, potem naglowek, potem zwykly ---
    const candidates = visible.filter(
      (b) => b.originalXml && textOf(b.originalXml).trim().length > 3,
    )
    const rank = (t: string) => (t === 'listItem' ? 0 : t === 'heading' ? 1 : t === 'paragraph' ? 2 : 3)
    candidates.sort((a, b) => rank(a.type) - rank(b.type))
    const target = candidates[0]
    if (!target) {
      row.note = 'brak akapitu z tekstem'
      rows.push(row)
      continue
    }
    row.note = `cel=${target.type}`

    const origXml = target.originalXml as string
    const patched = patchParagraphTexts(origXml, textOf(origXml) + SUFFIX)
    if (patched === null) {
      row.note += ' patch=null(fallback)'
      rows.push(row)
      continue
    }

    const finalBlocks: SaveBlock[] = visible.map((b) =>
      b.docxIndex === target.docxIndex
        ? { kind: 'xml', xml: patched, docxIndex: b.docxIndex as number }
        : { kind: 'original', docxIndex: b.docxIndex as number },
    )
    const saved = await saveDocx(doc, finalBlocks)

    // ktore wpisy ZIP sie zmienily
    const before = await entryHashes(input)
    const after = await entryHashes(saved)
    const sameKeys =
      [...before.keys()].sort().join('|') === [...after.keys()].sort().join('|')
    const changed = [...before.entries()]
      .filter(([k, v]) => after.get(k) !== v)
      .map(([k]) => k)
      .sort()
    row.zipDelta = !sameKeys
      ? 'ZMIANA ZESTAWU WPISOW'
      : changed.length === 1 && changed[0] === 'word/document.xml'
        ? 'tylko document.xml'
        : `INNE: ${changed.join(',')}`

    // ile pozostalych akapitow zachowalo dokladny oryginalny XML
    const newDocXml = await (await JSZip.loadAsync(saved))
      .file('word/document.xml')!
      .async('string')
    const others = visible.filter((b) => b.docxIndex !== target.docxIndex && b.originalXml)
    const kept = others.filter((b) => newDocXml.includes(b.originalXml as string)).length
    row.paraKept = `${kept}/${others.length}${kept === others.length ? ' OK' : ' UBYTEK'}`

    // czy w:pPr (styl + numeracja) edytowanego akapitu przetrwal
    const pOld = firstPPr(origXml)
    const pNew = firstPPr(patched)
    row.pPr = pOld === null ? 'brak w:pPr' : pOld === pNew ? 'OK' : 'ZMIENIONY'

    // czy w:rPr przetrwaly
    const rOld = allRPr(origXml)
    const rNew = allRPr(patched)
    row.rPr =
      rOld.length === 0
        ? 'brak w:rPr'
        : rOld.length === rNew.length && rOld.every((x, i) => x === rNew[i])
          ? `OK (${rOld.length})`
          : `ZMIENIONE ${rOld.length}->${rNew.length}`

    // reparse
    const re = await parseDocx(saved)
    const reVisible = re.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    const reTarget = reVisible.find((b) => b.docxIndex === target.docxIndex)
    const styleSame = reTarget?.styleId === target.styleId
    const listSame =
      JSON.stringify(reTarget?.list ?? null) === JSON.stringify(target.list ?? null)
    row.reparse =
      reVisible.length === visible.length && styleSame && listSame
        ? 'OK'
        : `bloki ${reVisible.length}/${visible.length} styl=${styleSame} lista=${listSame}`
  } catch (e) {
    row.note = `BLAD: ${(e as Error).message.slice(0, 60)}`
  }
  rows.push(row)
}

const cols: Array<keyof Row> = [
  'file',
  'blocks',
  'noop',
  'zipDelta',
  'paraKept',
  'pPr',
  'rPr',
  'reparse',
  'note',
]
console.log(cols.join('\t'))
for (const r of rows) console.log(cols.map((c) => String(r[c])).join('\t'))

// podsumowanie
const n = rows.length
const ok = (f: (r: Row) => boolean) => rows.filter(f).length
console.log('')
console.log(`PLIKOW: ${n}`)
console.log(`  no-op bajt-w-bajt OK:            ${ok((r) => r.noop === 'OK')}/${n}`)
console.log(`  zmienil sie tylko document.xml:  ${ok((r) => r.zipDelta === 'tylko document.xml')}/${n}`)
console.log(`  wszystkie inne akapity nietkniete: ${ok((r) => r.paraKept.endsWith('OK'))}/${n}`)
console.log(`  w:pPr edytowanego akapitu OK:    ${ok((r) => r.pPr === 'OK' || r.pPr === 'brak w:pPr')}/${n}`)
console.log(`  w:rPr OK:                        ${ok((r) => r.rPr.startsWith('OK') || r.rPr === 'brak w:rPr')}/${n}`)
console.log(`  reparse OK:                      ${ok((r) => r.reparse === 'OK')}/${n}`)
console.log(`  bledy:                           ${ok((r) => r.note.startsWith('BLAD'))}/${n}`)
