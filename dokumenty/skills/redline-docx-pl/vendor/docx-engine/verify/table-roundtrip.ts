/**
 * POMIAR B - wiernosc round-tripu przy edycji KOMORKI TABELI (patchTableCellTexts).
 *
 * Odpowiednik verify/roundtrip-real.ts, tylko celem jest komorka tabeli, a nie akapit.
 * Spike z 2026-08-05 tabel nie objal - jeden z 56 plikow zostal wtedy pominiety wlasnie
 * dlatego, ze harness trafil w tabele, a patchParagraphTexts obsluguje akapit.
 *
 * RODO / tajemnica adwokacka: skrypt NIE wypisuje ani jednego znaku tresci dokumentu
 * ANI nazwy pliku (nazwy pism niosa nazwiska stron). Kazdy plik dostaje id `fNN`.
 * Na stdout ida wylacznie liczniki, nazwy techniczne XML/ZIP i werdykty.
 *
 * Scenariusz na kazdym pliku majacym tabele:
 *   1. parse -> wybor tabeli i komorki z tekstem (preferowana komorka spoza 1. wiersza)
 *   2. patchTableCellTexts na oryginalnym XML tabeli (dopisek do tekstu 1. akapitu komorki)
 *   3. saveDocx z ta jedna tabela podmieniona jako {kind:'xml'}
 *   4. metryki: delta wpisow ZIP, ile innych blokow bajt-identycznych, ile innych
 *      komorek bajt-identycznych, czy tblPr/tblGrid/trPr/tcPr/pPr/rPr przetrwaly,
 *      czy po ponownym parsowaniu wymiary tabeli i tekst komorki sa zgodne z zamierzeniem
 *
 * Uzycie:
 *   npx tsx verify/table-roundtrip.ts sciezka/do/*.docx
 */
import JSZip from 'jszip'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { parseDocx, saveDocx, patchTableCellTexts, type SaveBlock } from '../src/index'

const SUFFIX = ' [ZMIANA TESTOWA ąćęłńóśźż]'

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

/** top-level segmenty `tag` w [from,to), swiadome zagniezdzenia.
 *  KOPIA 1:1 helpera z src/generate.ts (tam nie jest eksportowany). Kopia musi byc
 *  doslowna - inaczej harness mierzylby wlasny blad zamiast silnika. */
function xmlSegments(
  xml: string,
  tag: string,
  from: number,
  to: number,
): Array<{ start: number; end: number }> {
  const openPrefix = '<' + tag
  const closeTag = '</' + tag + '>'
  const segs: Array<{ start: number; end: number }> = []
  let depth = 0
  let segStart = -1
  let i = from
  while (i < to) {
    const o = xml.indexOf(openPrefix, i)
    const c = xml.indexOf(closeTag, i)
    if (c === -1 || c >= to) break
    if (o !== -1 && o < c) {
      const after = xml.charAt(o + openPrefix.length)
      if (after !== '>' && after !== ' ' && after !== '/') {
        i = o + openPrefix.length
        continue
      }
      const gt = xml.indexOf('>', o)
      if (gt !== -1 && xml.charAt(gt - 1) === '/') {
        if (depth === 0) segs.push({ start: o, end: gt + 1 })
        i = gt + 1
        continue
      }
      if (depth === 0) segStart = o
      depth++
      i = o + openPrefix.length
    } else {
      depth--
      if (depth === 0) segs.push({ start: segStart, end: c + closeTag.length })
      if (depth < 0) break
      i = c + closeTag.length
    }
  }
  return segs
}

function cellSlices(tableXml: string): string[] {
  const out: string[] = []
  for (const tr of xmlSegments(tableXml, 'w:tr', 0, tableXml.length)) {
    for (const tc of xmlSegments(tableXml, 'w:tc', tr.start, tr.end)) {
      out.push(tableXml.slice(tc.start, tc.end))
    }
  }
  return out
}

function firstTag(xml: string, tag: string): string | null {
  const re = new RegExp(`<${tag}(?:\\s[^>]*)?>[\\s\\S]*?</${tag}>|<${tag}(?:\\s[^>]*)?/>`)
  const m = re.exec(xml)
  return m ? m[0] : null
}

function allTags(xml: string, tag: string): string[] {
  const re = new RegExp(`<${tag}(?:\\s[^>]*)?>[\\s\\S]*?</${tag}>|<${tag}(?:\\s[^>]*)?/>`, 'g')
  return xml.match(re) ?? []
}

/** ile razy wystepuje element otwierajacy `tag` (bez mylenia z dluzszym prefiksem, np. w:r vs w:rPr) */
function countOpen(xml: string, tag: string): number {
  const re = new RegExp(`<${tag}(?=[\\s/>])`, 'g')
  return (xml.match(re) ?? []).length
}

/** konstrukty OOXML, ktore w komorce nie sa czystym tekstem - jesli znikaja, znika tresc/kotwica */
const CONSTRUCTS = [
  'w:hyperlink',
  'w:bookmarkStart',
  'w:commentRangeStart',
  'w:footnoteReference',
  'w:endnoteReference',
  'w:drawing',
  'w:fldSimple',
  'w:instrText',
  'w:br',
  'w:tab',
  'w:txbxContent',
  'w:pict',
  'w:object',
  'w:ins',
  'w:del',
  'w:sdt',
]

/** laczna DLUGOSC tekstu w w:t (sama liczba znakow, nigdy tresc) */
function textLen(xml: string): number {
  let n = 0
  const re = /<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g
  let m: RegExpExecArray | null
  while ((m = re.exec(xml)) !== null) n += m[1].length
  return n
}

/** raport "co ubylo": lista nazw elementow, ktorych liczba spadla (bez wartosci tekstowych) */
function constructLoss(oldXml: string, newXml: string): string {
  const lost: string[] = []
  for (const tag of CONSTRUCTS) {
    const a = countOpen(oldXml, tag)
    const b = countOpen(newXml, tag)
    if (b < a) lost.push(`${tag}:${a}->${b}`)
  }
  return lost.length === 0 ? 'brak strat' : lost.join(' ')
}

interface Row {
  id: string
  tables: number | string
  cells: string
  target: string
  zipDelta: string
  blocksKept: string
  cellsKept: string
  tblPr: string
  tblGrid: string
  trPr: string
  tcPr: string
  pPr: string
  rPr: string
  /** liczba runow w edytowanej komorce przed->po (rebuild splaszcza je do 1/akapit) */
  runs: string
  /** czy KAZDY akapit komorki zachowal swoj wlasny w:pPr (rebuild kopiuje pPr pierwszego) */
  cellPPr: string
  /** model=liczba akapitow w modelu, xml=liczba w:p przed->po */
  paras: string
  /** dlugosc tekstu w w:t komorki przed->po, i ile widzi model (same liczby znakow) */
  txtLen: string
  /** diagnostyka celu: scalenia, tabela zagniezdzona, siatka w:tc wg XML */
  cellDiag: string
  /** dlugosc tekstu wg TableCell.paras vs wg TableCell.richParas (rozjazd = paras niesie
   *  biale znaki formatowania XML, ktore patchTableCellTexts wpisuje do komorki jako TRESC) */
  parasVsRuns: string
  /** ile komorek WSZYSTKICH tabel pliku ma rozjazd paras vs richParas (populacja ryzyka) */
  wsXml: string
  /** konstrukty OOXML utracone w edytowanej komorce */
  lost: string
  /** ile komorek tego pliku ma mieszane formatowanie runow (ekspozycja na splaszczenie) */
  mixed: string
  reparse: string
  note: string
}

const rows: Row[] = []
let idx = 0

for (const f of process.argv.slice(2)) {
  idx++
  const id = `f${String(idx).padStart(2, '0')}`
  const row: Row = {
    id,
    tables: '-',
    cells: '-',
    target: '-',
    zipDelta: '-',
    blocksKept: '-',
    cellsKept: '-',
    tblPr: '-',
    tblGrid: '-',
    trPr: '-',
    tcPr: '-',
    pPr: '-',
    rPr: '-',
    runs: '-',
    paras: '-',
    txtLen: '-',
    cellDiag: '-',
    parasVsRuns: '-',
    wsXml: '-',
    cellPPr: '-',
    lost: '-',
    mixed: '-',
    reparse: '-',
    note: '',
  }
  try {
    const input = new Uint8Array(await readFile(f))
    const doc = await parseDocx(input)
    const visible = doc.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    const tables = visible.filter((b) => b.type === 'table' && b.originalXml && b.table)
    row.tables = tables.length
    if (tables.length === 0) {
      row.note = 'brak tabeli'
      rows.push(row)
      continue
    }

    // cel: pierwsza tabela z komorka niosaca tekst; preferowany wiersz > 1 (nie naglowek)
    let target: { block: (typeof tables)[number]; r: number; c: number } | null = null
    for (const t of tables) {
      const grid = t.table!.rows
      let best: { r: number; c: number } | null = null
      for (let r = 0; r < grid.length; r++) {
        for (let c = 0; c < grid[r].length; c++) {
          const cell = grid[r][c]
          if (cell.vMerge === 'continue') continue
          if (!cell.paras || cell.paras.length === 0) continue
          if ((cell.paras[0] ?? '').trim().length < 3) continue
          if (best === null || (best.r === 0 && r > 0)) best = { r, c }
          if (r > 0) break
        }
        if (best && best.r > 0) break
      }
      if (best) {
        target = { block: t, r: best.r, c: best.c }
        break
      }
    }
    if (!target) {
      row.note = 'brak komorki z tekstem'
      rows.push(row)
      continue
    }

    const tblXml = target.block.originalXml as string
    const grid = target.block.table!.rows
    row.cells = String(grid.reduce((n, r) => n + r.length, 0))
    row.target = `r${target.r}c${target.c}/${grid.length}x${grid[target.r].length}`

    // ekspozycja: ile komorek WE WSZYSTKICH tabelach pliku ma >1 rozny w:rPr albo >1 rozny w:pPr
    // (takie komorki traca formatowanie, jesli ktos je zedytuje - patrz kolumny runs/rPr/cellPPr)
    let mixedCells = 0
    let allCells = 0
    for (const t of tables) {
      for (const tc of cellSlices(t.originalXml as string)) {
        allCells++
        const rp = new Set(allTags(tc, 'w:rPr'))
        const pp = new Set(allTags(tc, 'w:pPr'))
        if (rp.size > 1 || pp.size > 1) mixedCells++
      }
    }
    row.mixed = `${mixedCells}/${allCells}`

    // ekspozycja na rozjazd paras vs richParas we WSZYSTKICH komorkach tabel pliku
    let polluted = 0
    let modelCells = 0
    for (const t of tables) {
      for (const rr of t.table!.rows) {
        for (const cc of rr) {
          modelCells++
          const pl = cc.paras.join('').length
          const rl = (cc.richParas ?? []).reduce(
            (n, rp) => n + rp.runs.reduce((m, r) => m + (r.text?.length ?? 0), 0),
            0,
          )
          if (pl !== rl) polluted++
        }
      }
    }
    row.wsXml = `${polluted}/${modelCells}`

    // siatka patcha: tylko komorka celu, reszta null
    const texts = grid.map((rowCells, r) =>
      rowCells.map((cell, c) =>
        r === target!.r && c === target!.c
          ? [(cell.paras[0] ?? '') + SUFFIX, ...cell.paras.slice(1)]
          : null,
      ),
    )
    {
      const tc = grid[target.r][target.c]
      const xmlTcPerRow = xmlSegments(tblXml, 'w:tr', 0, tblXml.length).map(
        (tr) => xmlSegments(tblXml, 'w:tc', tr.start, tr.end).length,
      )
      row.cellDiag =
        `vM=${tc.vMerge ?? '-'} hM=${tc.hMerge ?? '-'} cs=${tc.colSpan ?? '-'}` +
        ` nest=${tc.nestedTables?.length ?? 0} wt=${countOpen(target.block.originalXml as string, 'w:t')}` +
        ` modelWiersze=[${grid.map((r) => r.length).join(',')}]` +
        ` xmlWiersze=[${xmlTcPerRow.join(',')}]`
    }

    // rozjazd dwoch widokow modelu na te sama komorke
    {
      const tc = grid[target.r][target.c]
      const parasLen = tc.paras.join('').length
      const runsLen = (tc.richParas ?? []).reduce(
        (n, rp) => n + rp.runs.reduce((m, r) => m + (r.text?.length ?? 0), 0),
        0,
      )
      row.parasVsRuns = `${parasLen}/${runsLen}${parasLen === runsLen ? ' OK' : ' ROZJAZD'}`
    }

    const patched = patchTableCellTexts(tblXml, texts)
    if (patched === tblXml) {
      row.note = 'patch=NO-OP (XML tabeli nietkniety)'
      rows.push(row)
      continue
    }

    const finalBlocks: SaveBlock[] = visible.map((b) =>
      b.docxIndex === target!.block.docxIndex
        ? { kind: 'xml', xml: patched, docxIndex: b.docxIndex as number }
        : { kind: 'original', docxIndex: b.docxIndex as number },
    )
    const saved = await saveDocx(doc, finalBlocks)

    // --- delta wpisow ZIP ---
    const before = await entryHashes(input)
    const after = await entryHashes(saved)
    const sameKeys = [...before.keys()].sort().join('|') === [...after.keys()].sort().join('|')
    const changed = [...before.entries()]
      .filter(([k, v]) => after.get(k) !== v)
      .map(([k]) => k)
      .sort()
    const contentChanged = changed.filter((k) => k !== 'docProps/core.xml')
    row.zipDelta = !sameKeys
      ? 'ZMIANA ZESTAWU WPISOW'
      : contentChanged.length === 1 && contentChanged[0] === 'word/document.xml'
        ? changed.length === 1
          ? 'tylko document.xml'
          : 'document.xml + core.xml'
        : `INNE: ${contentChanged.join(',')}`

    // --- ile innych blokow zachowalo oryginalny XML ---
    const newDocXml = await (await JSZip.loadAsync(saved)).file('word/document.xml')!.async('string')
    const others = visible.filter((b) => b.docxIndex !== target!.block.docxIndex && b.originalXml)
    const kept = others.filter((b) => newDocXml.includes(b.originalXml as string)).length
    row.blocksKept = `${kept}/${others.length}${kept === others.length ? ' OK' : ' UBYTEK'}`

    // --- ile innych komorek tej tabeli zachowalo bajty ---
    const oldCells = cellSlices(tblXml)
    const newCells = cellSlices(patched)
    if (oldCells.length !== newCells.length) {
      row.cellsKept = `LICZBA KOMOREK ${oldCells.length}->${newCells.length}`
    } else {
      const same = oldCells.filter((x, i) => x === newCells[i]).length
      // dokladnie jedna komorka (cel) ma prawo sie roznic
      row.cellsKept = `${same}/${oldCells.length - 1}${same === oldCells.length - 1 ? ' OK' : same === oldCells.length ? ' NIC NIE ZMIENIONE' : ' UBYTEK'}`
    }

    // --- struktura tabeli ---
    const oTblPr = firstTag(tblXml, 'w:tblPr')
    const nTblPr = firstTag(patched, 'w:tblPr')
    row.tblPr = oTblPr === null ? 'brak' : oTblPr === nTblPr ? 'OK' : 'ZMIENIONY'
    const oGrid = firstTag(tblXml, 'w:tblGrid')
    const nGrid = firstTag(patched, 'w:tblGrid')
    row.tblGrid = oGrid === null ? 'brak' : oGrid === nGrid ? 'OK' : 'ZMIENIONY'
    const oTrPr = allTags(tblXml, 'w:trPr')
    const nTrPr = allTags(patched, 'w:trPr')
    row.trPr =
      oTrPr.length === 0
        ? 'brak'
        : oTrPr.length === nTrPr.length && oTrPr.every((x, i) => x === nTrPr[i])
          ? `OK (${oTrPr.length})`
          : `ZMIENIONE ${oTrPr.length}->${nTrPr.length}`

    // --- edytowana komorka: tcPr / pPr / rPr ---
    const oCell = oldCells.find((x, i) => x !== newCells[i])
    const oCellIdx = oldCells.findIndex((x, i) => x !== newCells[i])
    const nCell = oCellIdx >= 0 ? newCells[oCellIdx] : null
    if (!oCell || !nCell) {
      row.tcPr = row.pPr = row.rPr = 'brak zmienionej komorki'
    } else {
      const oTcPr = firstTag(oCell, 'w:tcPr')
      const nTcPr = firstTag(nCell, 'w:tcPr')
      row.tcPr = oTcPr === null ? 'brak' : oTcPr === nTcPr ? 'OK' : 'ZMIENIONY'
      const oPPr = firstTag(oCell, 'w:pPr')
      const nPPr = firstTag(nCell, 'w:pPr')
      row.pPr = oPPr === null ? 'brak' : oPPr === nPPr ? 'OK' : 'ZMIENIONY'
      const oRPr = allTags(oCell, 'w:rPr')
      const nRPr = allTags(nCell, 'w:rPr')
      row.rPr =
        oRPr.length === 0
          ? 'brak'
          : oRPr.length === nRPr.length && oRPr.every((x, i) => x === nRPr[i])
            ? `OK (${oRPr.length})`
            : `ZMIENIONE ${oRPr.length}->${nRPr.length}`

      // splaszczenie runow: patchCellXml odbudowuje komorke jako 1 run na akapit
      row.runs = `${countOpen(oCell, 'w:r')}->${countOpen(nCell, 'w:r')}`

      // czy KAZDY akapit komorki zachowal swoj wlasny pPr (rebuild kopiuje pPr pierwszego akapitu)
      const oPs = allTags(oCell, 'w:p')
      const nPs = allTags(nCell, 'w:p')
      const oAllPPr = oPs.map((p) => firstTag(p, 'w:pPr') ?? '')
      const nAllPPr = nPs.map((p) => firstTag(p, 'w:pPr') ?? '')
      // model widzi N akapitow, XML komorki ma M elementow w:p - rozjazd oznacza,
      // ze czesc akapitow zyje poza modelem (np. w polu tekstowym) i rebuild ja gubi
      row.paras = `model=${grid[target.r][target.c].paras.length} xml=${countOpen(oCell, 'w:p')}->${countOpen(nCell, 'w:p')}`
      row.txtLen = `${textLen(oCell)}->${textLen(nCell)} model=${grid[target.r][target.c].paras.join('').length}`
      row.cellPPr =
        oPs.length !== nPs.length
          ? `LICZBA AKAPITOW ${oPs.length}->${nPs.length}`
          : oAllPPr.every((x, i) => x === nAllPPr[i])
            ? `OK (${oPs.length})`
            : `ROZJECHANE ${oAllPPr.filter((x, i) => x !== nAllPPr[i]).length}/${oPs.length}`

      row.lost = constructLoss(oCell, nCell)
    }

    // --- reparse: wymiary tabeli i czy tekst komorki faktycznie sie zmienil zgodnie z zamiarem ---
    const re = await parseDocx(saved)
    const reVisible = re.blocks.filter((b) => !b.hidden && b.docxIndex !== null)
    const reTbl = reVisible.find((b) => b.docxIndex === target!.block.docxIndex)
    const reGrid = reTbl?.table?.rows
    const dimsSame =
      !!reGrid &&
      reGrid.length === grid.length &&
      reGrid.every((r, i) => r.length === grid[i].length)
    const expected = (grid[target.r][target.c].paras[0] ?? '') + SUFFIX
    const gotText = reGrid?.[target.r]?.[target.c]?.paras?.[0] ?? null
    const textApplied = gotText === expected
    const otherCellsSame =
      !!reGrid &&
      dimsSame &&
      reGrid.every((r, ri) =>
        r.every(
          (cell, ci) =>
            (ri === target!.r && ci === target!.c) ||
            JSON.stringify(cell.paras) === JSON.stringify(grid[ri][ci].paras),
        ),
      )
    row.reparse =
      reVisible.length === visible.length && dimsSame && textApplied && otherCellsSame
        ? 'OK'
        : `bloki=${reVisible.length}/${visible.length} wymiary=${dimsSame} tekst=${textApplied}` +
          // dlugosci zamiast tresci: diagnoza rozjazdu bez wypisywania pisma
          (textApplied ? '' : `(dlug ocz=${expected.length} jest=${gotText === null ? 'null' : gotText.length} akapitow=${grid[target.r][target.c].paras.length})`) +
          ` inne=${otherCellsSame}`
  } catch (e) {
    row.note = `BLAD: ${(e as Error).message.slice(0, 60)}`
  }
  rows.push(row)
}

const cols: Array<keyof Row> = [
  'id',
  'tables',
  'cells',
  'target',
  'zipDelta',
  'blocksKept',
  'cellsKept',
  'tblPr',
  'tblGrid',
  'trPr',
  'tcPr',
  'pPr',
  'rPr',
  'runs',
  'paras',
  'txtLen',
  'cellDiag',
  'parasVsRuns',
  'wsXml',
  'cellPPr',
  'lost',
  'mixed',
  'reparse',
  'note',
]
console.log(cols.join('\t'))
for (const r of rows) console.log(cols.map((c) => String(r[c])).join('\t'))

const withTable = rows.filter((r) => r.tables !== '-' && Number(r.tables) > 0)
const measured = withTable.filter((r) => r.reparse !== '-')
const n = measured.length
const ok = (f: (r: Row) => boolean) => measured.filter(f).length
console.log('')
console.log(`PLIKOW WEJSCIOWYCH:        ${rows.length}`)
console.log(`  z tabela:                ${withTable.length}`)
console.log(`  zmierzonych (patch ruszyl): ${n}`)
console.log(`  zmienil sie tylko document.xml (+core): ${ok((r) => r.zipDelta.startsWith('tylko') || r.zipDelta.startsWith('document.xml +'))}/${n}`)
console.log(`  wszystkie inne bloki nietkniete:        ${ok((r) => r.blocksKept.endsWith('OK'))}/${n}`)
console.log(`  wszystkie inne komorki bajt-identyczne: ${ok((r) => r.cellsKept.endsWith('OK'))}/${n}`)
console.log(`  w:tblPr nietkniety:      ${ok((r) => r.tblPr === 'OK' || r.tblPr === 'brak')}/${n}`)
console.log(`  w:tblGrid nietkniety:    ${ok((r) => r.tblGrid === 'OK' || r.tblGrid === 'brak')}/${n}`)
console.log(`  w:trPr nietkniete:       ${ok((r) => r.trPr.startsWith('OK') || r.trPr === 'brak')}/${n}`)
console.log(`  w:tcPr celu nietkniety:  ${ok((r) => r.tcPr === 'OK' || r.tcPr === 'brak')}/${n}`)
console.log(`  w:pPr celu nietkniety:   ${ok((r) => r.pPr === 'OK' || r.pPr === 'brak')}/${n}`)
console.log(`  w:rPr celu nietkniete:   ${ok((r) => r.rPr.startsWith('OK') || r.rPr === 'brak')}/${n}`)
console.log(`  liczba runow celu bez zmian: ${ok((r) => { const [a, b] = r.runs.split('->'); return a === b })}/${n}`)
console.log(`  pPr KAZDEGO akapitu celu OK: ${ok((r) => r.cellPPr.startsWith('OK'))}/${n}`)
console.log(`  bez utraty konstruktow:  ${ok((r) => r.lost === 'brak strat')}/${n}`)
console.log(`  paras vs richParas zgodne: ${ok((r) => r.parasVsRuns.endsWith('OK'))}/${n}`)
console.log(`  reparse OK (tekst komorki taki, jak zamierzony): ${ok((r) => r.reparse === 'OK')}/${n}`)
console.log(`  bledy:                   ${rows.filter((r) => r.note.startsWith('BLAD')).length}/${rows.length}`)

// ekspozycja korpusu na splaszczenie: ile komorek ma mieszane formatowanie
let mixTot = 0
let cellTot = 0
for (const r of withTable) {
  const m = /^(\d+)\/(\d+)$/.exec(r.mixed)
  if (m) {
    mixTot += Number(m[1])
    cellTot += Number(m[2])
  }
}
console.log(
  `  EKSPOZYCJA A: komorek z mieszanym formatowaniem w korpusie: ${mixTot}/${cellTot}` +
    (cellTot ? ` (${Math.round((mixTot / cellTot) * 100)}%)` : ''),
)
let polTot = 0
let polCells = 0
let polFiles = 0
for (const r of withTable) {
  const m = /^(\d+)\/(\d+)$/.exec(r.wsXml)
  if (m) {
    polTot += Number(m[1])
    polCells += Number(m[2])
    if (Number(m[1]) > 0) polFiles++
  }
}
console.log(
  `  EKSPOZYCJA B: komorek z rozjazdem paras vs richParas: ${polTot}/${polCells}` +
    (polCells ? ` (${Math.round((polTot / polCells) * 100)}%)` : '') +
    ` w ${polFiles}/${withTable.length} plikach z tabela`,
)
