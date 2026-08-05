// Sonda struktury .docx - RAPORTUJE WYLACZNIE METRYKI STRUKTURALNE.
// Zadna tresc dokumentu nie jest wypisywana (tajemnica adwokacka / RODO).
import JSZip from 'jszip'
import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'

const files = process.argv.slice(2)

for (const f of files) {
  try {
    const buf = await readFile(f)
    const zip = await JSZip.loadAsync(buf)
    const names = Object.keys(zip.files)
    const doc = await zip.file('word/document.xml')?.async('string')
    if (!doc) {
      console.log(`${basename(f)}\tBRAK word/document.xml`)
      continue
    }
    // liczby, nie tresc
    const count = (re) => (doc.match(re) || []).length
    const paras = count(/<w:p[ >]/g)
    const headings = count(/w:val="(Heading|Nag)[^"]*"/g)
    const numPr = count(/<w:numPr>/g)
    const footRefs = count(/<w:footnoteReference /g)
    const endRefs = count(/<w:endnoteReference /g)
    const tables = count(/<w:tbl>/g)
    const hasFootnotesPart = names.includes('word/footnotes.xml')
    const hasNumberingPart = names.includes('word/numbering.xml')
    console.log(
      [
        basename(f),
        `kB=${Math.round(buf.length / 1024)}`,
        `wpisyZIP=${names.length}`,
        `akapity=${paras}`,
        `naglowki=${headings}`,
        `numPr=${numPr}`,
        `przypisyDolne=${footRefs}`,
        `przypisyKoncowe=${endRefs}`,
        `tabele=${tables}`,
        `footnotes.xml=${hasFootnotesPart}`,
        `numbering.xml=${hasNumberingPart}`,
      ].join('\t')
    )
  } catch (e) {
    console.log(`${basename(f)}\tBLAD: ${e.message}`)
  }
}
