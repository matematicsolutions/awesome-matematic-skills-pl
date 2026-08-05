/**
 * POMIAR A - sciezka `revision` silnika wobec `uvx adeu apply`, na TYM SAMYM pismie.
 *
 * Spike z 2026-08-05 mierzyl wiernosc round-tripu, NIE generowanie natywnych Word
 * Track Changes. Track Changes to rdzen wartosci skilla `redline-docx-pl`, wiec
 * zanim silnik wejdzie w workflow, musi byc zmierzony wlasnie tutaj.
 *
 * Silnik ma DWIE rozne drogi do sledzonej zmiany i obie sa mierzone osobno:
 *   V1 - `SaveBlock.revision` (opakowanie CALEGO bloku: <w:ins><w:p>...</w:p></w:ins>)
 *   V2 - `Run.ins` / `Run.del` w regenerowanym akapicie (<w:ins><w:r><w:t>,
 *        <w:del><w:r><w:delText>) - to jest konstrukcja, ktorej uzywa Word
 * ADEU - `uvx adeu apply` z edits.json (dzisiejsza produkcja skilla), jako punkt odniesienia.
 *
 * ORAKULA (Worda na tej maszynie nie ma, wiec werdykt opiera sie na trzech
 * niezaleznych czytnikach zamiast na jednym):
 *   1. struktura OOXML - element nadrzedny kazdego w:ins/w:del, atrybuty autora/daty,
 *      w:delText kontra w:t w srodku w:del (Word wymaga w:delText)
 *   2. `uvx adeu extract` na WYNIKU silnika - czy niezalezny czytnik OOXML widzi
 *      zmiane jako sledzona (CriticMarkup {++ ++} / {-- --})
 *   3. LibreOffice --convert-to fodt - ile regionow sledzonej zmiany widzi
 *      niezalezna implementacja (wlacz przez LO=1)
 *
 * RODO / tajemnica adwokacka: skrypt NIE wypisuje ani jednego znaku tresci dokumentu
 * ANI nazwy pliku. Kazdy plik dostaje id `fNN`. Na stdout ida wylacznie liczniki,
 * nazwy elementow XML i werdykty. Pliki posrednie zyja w katalogu tymczasowym
 * systemu i sa kasowane po pomiarze.
 *
 * Uzycie:
 *   npx tsx verify/revision-vs-adeu.ts sciezka/do/*.docx
 *   LO=1 npx tsx verify/revision-vs-adeu.ts sciezka/do/plik.docx     # + orakul LibreOffice
 */
import JSZip from 'jszip'
import { spawnSync } from 'node:child_process'
import { mkdtempSync, rmSync, writeFileSync, readFileSync, readdirSync, existsSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { parseDocx, saveDocx, type SaveBlock } from '../src/index'
import type { Run } from '../src/types'

const SUFFIX = ' ZMIANA TESTOWA'
const AUTHOR = 'MateMatic Pomiar'
const DATE = '2026-08-05T12:00:00Z'
const UVX = process.env.UVX_BIN ?? 'C:\\Users\\Wieslaw\\.local\\bin\\uvx.exe'
const SOFFICE = process.env.SOFFICE_BIN ?? 'C:\\Program Files\\LibreOffice\\program\\soffice.exe'
const USE_LO = process.env.LO === '1'
/** SCAN=1: tylko odczyt - gdzie w PRAWDZIWYCH plikach z obrotu leza w:ins / w:del (zero zapisu) */
const SCAN_ONLY = process.env.SCAN === '1'

// ---------- pomocnicze: metryki strukturalne, zero tresci ----------

async function docXml(bytes: Uint8Array): Promise<string> {
  return (await JSZip.loadAsync(bytes)).file('word/document.xml')!.async('string')
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

interface RevSite {
  kind: 'ins' | 'del'
  /** nazwa elementu nadrzednego (w:body / w:p / w:rPr / w:trPr / w:tcPr ...) */
  parent: string
  hasAuthor: boolean
  hasDate: boolean
  hasId: boolean
  /** czy w srodku sa akapity (opakowanie blokowe) */
  wrapsParagraph: boolean
  /** liczba w:t i w:delText bezposrednio w srodku */
  wt: number
  wDelText: number
}

/**
 * Skan document.xml stosem tagow: dla kazdego w:ins / w:del ustala element nadrzedny
 * i to, co element obejmuje. Zwraca same nazwy i liczniki.
 */
function revisionSites(xml: string): RevSite[] {
  const out: RevSite[] = []
  const stack: string[] = []
  const re = /<(\/?)([A-Za-z0-9:]+)((?:"[^"]*"|[^>"])*?)(\/?)>/g
  let m: RegExpExecArray | null
  const open: Array<{ kind: 'ins' | 'del'; parent: string; attrs: string; start: number; depth: number }> = []
  while ((m = re.exec(xml)) !== null) {
    const closing = m[1] === '/'
    const name = m[2]
    const attrs = m[3]
    const selfClosing = m[4] === '/'
    if (closing) {
      stack.pop()
      const top = open[open.length - 1]
      if (top && name === `w:${top.kind}` && stack.length === top.depth) {
        open.pop()
        const inner = xml.slice(top.start, m.index)
        out.push({
          kind: top.kind,
          parent: top.parent,
          hasAuthor: /\sw:author=/.test(top.attrs),
          hasDate: /\sw:date=/.test(top.attrs),
          hasId: /\sw:id=/.test(top.attrs),
          wrapsParagraph: /<w:p[\s>]/.test(inner),
          wt: (inner.match(/<w:t[\s>]/g) ?? []).length,
          wDelText: (inner.match(/<w:delText[\s>]/g) ?? []).length,
        })
      }
      continue
    }
    if (!selfClosing) {
      if (name === 'w:ins' || name === 'w:del') {
        open.push({
          kind: name === 'w:ins' ? 'ins' : 'del',
          parent: stack[stack.length - 1] ?? '(root)',
          attrs,
          start: m.index + m[0].length,
          depth: stack.length,
        })
      }
      stack.push(name)
    }
  }
  return out
}

/** zwiezly opis miejsc rewizji: kind@parent xN, plus flagi */
function sitesSummary(sites: RevSite[]): string {
  if (sites.length === 0) return 'BRAK'
  const byKey = new Map<string, number>()
  for (const s of sites) {
    const key = `${s.kind}@${s.parent}${s.wrapsParagraph ? '(owija w:p)' : ''}`
    byKey.set(key, (byKey.get(key) ?? 0) + 1)
  }
  return [...byKey.entries()].map(([k, v]) => `${k}x${v}`).join(' ')
}

/** czy kazde w:del niesie tekst w w:delText, a nie w w:t (Word odrzuca w:t w w:del) */
function delTextVerdict(sites: RevSite[]): string {
  const dels = sites.filter((s) => s.kind === 'del' && !s.wrapsParagraph)
  const blockDels = sites.filter((s) => s.kind === 'del' && s.wrapsParagraph)
  if (dels.length === 0 && blockDels.length === 0) return 'brak w:del'
  const bad = [...dels, ...blockDels].filter((s) => s.wt > 0)
  return bad.length === 0
    ? `OK (delText w ${[...dels, ...blockDels].filter((s) => s.wDelText > 0).length}/${dels.length + blockDels.length})`
    : `w:t W SRODKU w:del: ${bad.length}/${dels.length + blockDels.length}`
}

function attrVerdict(sites: RevSite[]): string {
  if (sites.length === 0) return '-'
  const noAuthor = sites.filter((s) => !s.hasAuthor).length
  const noDate = sites.filter((s) => !s.hasDate).length
  const noId = sites.filter((s) => !s.hasId).length
  return noAuthor === 0 && noDate === 0 && noId === 0
    ? 'autor+data+id OK'
    : `brak autora:${noAuthor} daty:${noDate} id:${noId}`
}

// ---------- orakula zewnetrzne ----------

/** adeu extract -> ile znacznikow CriticMarkup wstawienia/usuniecia widzi niezalezny czytnik */
function adeuExtractMarkers(docxPath: string, dir: string, tag: string): string {
  const outMd = join(dir, `extract-${tag}.md`)
  const r = spawnSync(UVX, ['adeu', 'extract', docxPath, '--page', 'all', '-o', outMd], {
    encoding: 'utf8',
    windowsHide: true,
  })
  if (r.status !== 0 || !existsSync(outMd)) return `EXTRACT ERR(${r.status})`
  const md = readFileSync(outMd, 'utf8')
  const ins = (md.match(/\{\+\+/g) ?? []).length
  const del = (md.match(/\{--/g) ?? []).length
  return `ins=${ins} del=${del}`
}

/** LibreOffice -> fodt -> ile regionow sledzonej zmiany widzi niezalezna implementacja */
function loChangedRegions(docxPath: string, dir: string, tag: string): string {
  const outDir = join(dir, `lo-${tag}`)
  const r = spawnSync(
    SOFFICE,
    ['--headless', '--norestore', '--convert-to', 'fodt', '--outdir', outDir, docxPath],
    { encoding: 'utf8', windowsHide: true, timeout: 180000 },
  )
  if (!existsSync(outDir)) return `LO ERR(${r.status})`
  const files = readdirSync(outDir).filter((f) => f.endsWith('.fodt'))
  if (files.length === 0) return `LO BRAK WYJSCIA(${r.status})`
  const fodt = readFileSync(join(outDir, files[0]), 'utf8')
  const regions = (fodt.match(/<text:changed-region[\s>]/g) ?? []).length
  const ins = (fodt.match(/<text:insertion[\s>]/g) ?? []).length
  const del = (fodt.match(/<text:deletion[\s>]/g) ?? []).length
  return `regiony=${regions} ins=${ins} del=${del}`
}

// ---------- pomiar ----------

interface Row {
  id: string
  wariant: string
  ok: string
  /** rozmieszczenie w:ins / w:del w document.xml */
  miejsca: string
  atrybuty: string
  delText: string
  /** ile innych blokow zachowalo oryginalne bajty */
  inneBloki: string
  /** w:pPr celu bajt-identyczny */
  pPr: string
  /** liczba w:r i w:rPr w akapicie celu przed->po (splaszczenie runow przy regeneracji) */
  runy: string
  rPr: string
  /** czy KAZDY rozny w:rPr z oryginalnego akapitu wystepuje nadal w wyniku
   *  (spadek liczby runow moze byc scaleniem identycznie sformatowanych, a nie utrata) */
  rPrZbior: string
  /** silnik po ponownym otwarciu: runy z ins/del + bloki z blockRevision */
  reparse: string
  /** adeu extract na wyniku - CriticMarkup */
  adeu: string
  /** LibreOffice - regiony sledzonych zmian */
  lo: string
  note: string
}

const rows: Row[] = []

// --- tryb SCAN: rozklad miejsc w:ins/w:del w dokumentach, ktore wyprodukowal Word ---
if (SCAN_ONLY) {
  const tally = new Map<string, number>()
  let withRev = 0
  let scanned = 0
  let i = 0
  for (const f of process.argv.slice(2)) {
    i++
    try {
      const xml = await docXml(new Uint8Array(await readFile(f)))
      scanned++
      const sites = revisionSites(xml)
      if (sites.length > 0) withRev++
      for (const st of sites) {
        const key = `${st.kind}@${st.parent}${st.wrapsParagraph ? '(owija w:p)' : ''}`
        tally.set(key, (tally.get(key) ?? 0) + 1)
      }
    } catch {
      // plik nieczytelny - pomijamy, liczy sie rozklad, nie kompletnosc
    }
  }
  console.log(`SKAN plikow: ${scanned}, z rewizjami: ${withRev}`)
  console.log('miejsce	liczba')
  for (const [k, v] of [...tally.entries()].sort((a, b) => b[1] - a[1])) console.log(`${k}	${v}`)
  process.exit(0)
}

const tmp = mkdtempSync(join(tmpdir(), 'revmeas-'))
let idx = 0

try {
  for (const f of process.argv.slice(2)) {
    idx++
    const id = `f${String(idx).padStart(2, '0')}`
    const mk = (wariant: string): Row => ({
      id,
      wariant,
      ok: '-',
      miejsca: '-',
      atrybuty: '-',
      delText: '-',
      inneBloki: '-',
      pPr: '-',
      runy: '-',
      rPr: '-',
      rPrZbior: '-',
      reparse: '-',
      adeu: '-',
      lo: '-',
      note: '',
    })

    let input: Uint8Array
    let doc: Awaited<ReturnType<typeof parseDocx>>
    try {
      input = new Uint8Array(await readFile(f))
      doc = await parseDocx(input)
    } catch (e) {
      const r = mk('-')
      r.note = `BLAD PARSE: ${(e as Error).message.slice(0, 50)}`
      rows.push(r)
      continue
    }

    const visible = doc.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    // cel: akapit z tekstem >= 25 znakow, wystepujacy w dokumencie DOKLADNIE raz
    // (adeu w trybie strict blokuje niejednoznaczne dopasowanie - chcemy porownywac
    //  te sama zmiane, a nie roznice w bramce dopasowania)
    const wholeText = visible.map((b) => (b.originalXml ? textOf(b.originalXml) : '')).join('\n')
    const rank = (t: string) => (t === 'listItem' ? 0 : t === 'heading' ? 1 : t === 'paragraph' ? 2 : 3)
    const candidates = visible
      .filter((b) => b.originalXml && b.type !== 'table' && (b.runs?.length ?? 0) > 0)
      .filter((b) => {
        const t = textOf(b.originalXml as string).trim()
        return t.length >= 25 && wholeText.split(t).length === 2
      })
      .sort((a, b) => rank(a.type) - rank(b.type))
    const target = candidates[0]
    if (!target) {
      const r = mk('-')
      r.note = 'brak jednoznacznego akapitu >=25 znakow'
      rows.push(r)
      continue
    }
    const origXml = target.originalXml as string
    const origText = textOf(origXml).trim()
    const rPrBefore = (origXml.match(/<w:rPr[\s>]/g) ?? []).length
    const runsBefore = (origXml.match(/<w:r[\s>]/g) ?? []).length
    const rPrSetBefore = new Set(origXml.match(/<w:rPr[\s>][\s\S]*?<\/w:rPr>/g) ?? [])
    const pPrOld = /<w:pPr>[\s\S]*?<\/w:pPr>/.exec(origXml)?.[0] ?? null
    const others = visible.filter((b) => b.docxIndex !== target.docxIndex && b.originalXml)

    const revIns = { kind: 'ins' as const, author: AUTHOR, date: DATE, id: '9001' }
    const revDel = { kind: 'del' as const, author: AUTHOR, date: DATE, id: '9002' }

    /** wspolna ocena wyniku (bajty .docx) */
    const score = async (row: Row, bytes: Uint8Array, path: string, tag: string) => {
      const xml = await docXml(bytes)
      const sites = revisionSites(xml)
      row.miejsca = sitesSummary(sites)
      row.atrybuty = attrVerdict(sites)
      row.delText = delTextVerdict(sites)
      const kept = others.filter((b) => xml.includes(b.originalXml as string)).length
      row.inneBloki = `${kept}/${others.length}${kept === others.length ? ' OK' : ' UBYTEK'}`
      row.pPr = pPrOld === null ? 'brak w:pPr' : xml.includes(pPrOld) ? 'OK' : 'ZMIENIONY'
      // w:rPr liczone w calym document.xml celu jest nieporownywalne miedzy wariantami,
      // wiec liczymy w akapicie, ktory niesie nasz dopisek
      const paras = xml.match(/<w:p(?:\s[^>]*)?>[\s\S]*?<\/w:p>/g) ?? []
      const hit = paras.find((p) => textOf(p).includes(SUFFIX.trim()))
      row.rPr = `${rPrBefore}->${hit ? (hit.match(/<w:rPr[\s>]/g) ?? []).length : '?'}`
      row.runy = `${runsBefore}->${hit ? (hit.match(/<w:r[\s>]/g) ?? []).length : '?'}`
      if (!hit) row.rPrZbior = '?'
      else if (rPrSetBefore.size === 0) row.rPrZbior = 'brak w:rPr'
      else {
        const after = new Set(hit.match(/<w:rPr[\s>][\s\S]*?<\/w:rPr>/g) ?? [])
        const kept = [...rPrSetBefore].filter((x) => after.has(x)).length
        row.rPrZbior = `${kept}/${rPrSetBefore.size}${kept === rPrSetBefore.size ? ' OK' : ' UBYTEK'}`
      }
      try {
        const re = await parseDocx(bytes)
        const runIns = re.blocks.reduce(
          (n, b) => n + (b.runs?.filter((r) => r.ins).length ?? 0),
          0,
        )
        const runDel = re.blocks.reduce(
          (n, b) => n + (b.runs?.filter((r) => r.del).length ?? 0),
          0,
        )
        const blockRev = re.blocks.filter((b) => b.blockRevision).length
        row.reparse = `runIns=${runIns} runDel=${runDel} blockRev=${blockRev}`
      } catch (e) {
        row.reparse = `BLAD REPARSE: ${(e as Error).message.slice(0, 30)}`
      }
      row.adeu = adeuExtractMarkers(path, tmp, `${id}-${tag}`)
      if (USE_LO) row.lo = loChangedRegions(path, tmp, `${id}-${tag}`)
    }

    // ---------- V1: SaveBlock.revision (opakowanie blokowe) ----------
    {
      const row = mk('V1 blok')
      try {
        const genBlock = {
          type: (target.type === 'heading' || target.type === 'listItem'
            ? target.type
            : 'paragraph') as 'paragraph' | 'heading' | 'listItem',
          ...(target.level !== undefined ? { level: target.level } : {}),
          ...(target.styleId ? { styleId: target.styleId } : {}),
          ...(target.list ? { list: target.list } : {}),
          ...(target.rawPPr ? { rawPPr: target.rawPPr } : {}),
          runs: [{ text: origText + SUFFIX }] as Run[],
        }
        const blocks: SaveBlock[] = []
        for (const b of visible) {
          if (b.docxIndex === target.docxIndex) {
            blocks.push({ kind: 'xml', xml: origXml, docxIndex: b.docxIndex as number, revision: revDel })
            blocks.push({ kind: 'generated', block: genBlock, revision: revIns })
          } else {
            blocks.push({ kind: 'original', docxIndex: b.docxIndex as number })
          }
        }
        const out = await saveDocx(doc, blocks)
        const p = join(tmp, `${id}-v1.docx`)
        writeFileSync(p, out)
        row.ok = 'zapis OK'
        await score(row, out, p, 'v1')
      } catch (e) {
        row.ok = 'BLAD'
        row.note = (e as Error).message.slice(0, 60)
      }
      rows.push(row)
    }

    // ---------- V2: Run.ins / Run.del w regenerowanym akapicie ----------
    {
      const row = mk('V2 run')
      try {
        const runs = (target.runs ?? []).slice()
        const last = runs[runs.length - 1]
        const newRuns: Run[] = [
          ...runs.slice(0, -1),
          { ...last, del: { author: AUTHOR, date: DATE, id: '9012' } },
          {
            ...last,
            text: (last.text ?? '') + SUFFIX,
            ins: { author: AUTHOR, date: DATE, id: '9011' },
          },
        ]
        const genBlock = {
          type: (target.type === 'heading' || target.type === 'listItem'
            ? target.type
            : 'paragraph') as 'paragraph' | 'heading' | 'listItem',
          ...(target.level !== undefined ? { level: target.level } : {}),
          ...(target.styleId ? { styleId: target.styleId } : {}),
          ...(target.list ? { list: target.list } : {}),
          ...(target.rawPPr ? { rawPPr: target.rawPPr } : {}),
          runs: newRuns,
        }
        const blocks: SaveBlock[] = visible.map((b) =>
          b.docxIndex === target.docxIndex
            ? ({ kind: 'generated', block: genBlock } as SaveBlock)
            : ({ kind: 'original', docxIndex: b.docxIndex as number } as SaveBlock),
        )
        const out = await saveDocx(doc, blocks)
        const p = join(tmp, `${id}-v2.docx`)
        writeFileSync(p, out)
        row.ok = 'zapis OK'
        await score(row, out, p, 'v2')
      } catch (e) {
        row.ok = 'BLAD'
        row.note = (e as Error).message.slice(0, 60)
      }
      rows.push(row)
    }

    // ---------- ADEU: uvx adeu apply ----------
    {
      const row = mk('ADEU')
      try {
        const editsPath = join(tmp, `${id}-edits.json`)
        writeFileSync(
          editsPath,
          JSON.stringify([
            {
              type: 'modify',
              target_text: origText,
              new_text: origText + SUFFIX,
              match_mode: 'first',
            },
          ]),
          'utf8',
        )
        const outPath = join(tmp, `${id}-adeu.docx`)
        const r = spawnSync(
          UVX,
          ['adeu', 'apply', f, editsPath, '-o', outPath, '--author', AUTHOR, '--json'],
          { encoding: 'utf8', windowsHide: true, timeout: 300000 },
        )
        if (r.status !== 0 || !existsSync(outPath)) {
          row.ok = `BLAD APPLY(${r.status})`
          row.note = (r.stderr ?? '').split('\n').filter(Boolean).slice(-1)[0]?.slice(0, 60) ?? ''
        } else {
          row.ok = 'apply OK'
          const bytes = new Uint8Array(readFileSync(outPath))
          await score(row, bytes, outPath, 'adeu')
        }
      } catch (e) {
        row.ok = 'BLAD'
        row.note = (e as Error).message.slice(0, 60)
      }
      rows.push(row)
    }
  }

  const cols: Array<keyof Row> = [
    'id',
    'wariant',
    'ok',
    'miejsca',
    'atrybuty',
    'delText',
    'inneBloki',
    'pPr',
    'runy',
    'rPr',
    'rPrZbior',
    'reparse',
    'adeu',
    'lo',
    'note',
  ]
  console.log(cols.join('\t'))
  for (const r of rows) console.log(cols.map((c) => String(r[c])).join('\t'))

  console.log('')
  for (const w of ['V1 blok', 'V2 run', 'ADEU']) {
    const g = rows.filter((r) => r.wariant === w)
    if (g.length === 0) continue
    const n = g.length
    const cnt = (f: (r: Row) => boolean) => g.filter(f).length
    console.log(`WARIANT ${w} (${n} plikow)`)
    console.log(`  zapis/apply bez bledu:                 ${cnt((r) => r.ok.endsWith('OK'))}/${n}`)
    console.log(`  w:ins/w:del w ogole powstaly:          ${cnt((r) => r.miejsca !== 'BRAK' && r.miejsca !== '-')}/${n}`)
    console.log(`  autor + data + id na kazdym:           ${cnt((r) => r.atrybuty === 'autor+data+id OK')}/${n}`)
    const withDel = g.filter((r) => r.delText !== 'brak w:del' && r.delText !== '-')
    console.log(
      `  w:del niesie w:delText (nie w:t):      ${withDel.filter((r) => r.delText.startsWith('OK')).length}/${withDel.length}` +
        ` (w ${n - withDel.length} plikach w:del nie powstalo)`,
    )
    console.log(`  inne bloki bajt-identyczne:            ${cnt((r) => r.inneBloki.endsWith('OK'))}/${n}`)
    console.log(`  w:pPr celu bajt-identyczny:            ${cnt((r) => r.pPr === 'OK' || r.pPr === 'brak w:pPr')}/${n}`)
    console.log(`  kazdy rozny w:rPr celu zachowany:      ${cnt((r) => r.rPrZbior.endsWith('OK') || r.rPrZbior === 'brak w:rPr')}/${n}`)
    console.log(`  adeu extract widzi wstawienie:         ${cnt((r) => /ins=[1-9]/.test(r.adeu))}/${n}`)
    console.log(`  adeu extract widzi usuniecie:          ${cnt((r) => /del=[1-9]/.test(r.adeu))}/${n}`)
    if (USE_LO) {
      console.log(`  LibreOffice widzi region zmiany:       ${cnt((r) => /regiony=[1-9]/.test(r.lo))}/${n}`)
    }
    console.log('')
  }
} finally {
  rmSync(tmp, { recursive: true, force: true })
}
