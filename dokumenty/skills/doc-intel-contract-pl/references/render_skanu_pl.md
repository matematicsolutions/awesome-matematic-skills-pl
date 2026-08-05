# Render skanu PDF do obrazow (przed silnikiem OCR/VLM)

Przepis z datalab-to/chandra (Apache-2.0, `chandra/input.py`). Zaleznosc
pypdfium2 jest OPCJONALNA i lezy poza sciezka normalizacji kontraktu -
Article I (zero-cloud, zero-dep w normalizacji) nienaruszony.

## Kolejnosc obowiazkowa

Walidacje podpisu kwalifikowanego ([[waliduj-podpis-pdf-pl]]) rob PRZED
flatten, na oryginale pliku. Splaszczenie niszczy podpis kryptograficznie -
po flatten nie ma juz czego walidowac.

## Kroki

1. **Splaszcz formularze przed renderem**: `FPDFPage_Flatten` z pypdfium2
   (tryb `FLAT_NORMALDISPLAY`). AcroForm i adnotacje zostaja wypalone
   w obraz - bez tego pola formularza znikaja z renderu, a OCR czyta pusty
   dokument. Por. gotcha reference_pdf_acroform_baked_highlight_rects.
2. **DPI dynamiczne, nie stale**:
   `scale_dpi = max((1024 / krotszy_bok_strony_w_punktach) * 72, 192)`.
   Male strony nie wychodza nieczytelne, duze nie marnuja tokenow.
3. **Skany juz w formie obrazu** (JPG/PNG): upscale do min. 1536 px
   krotszego boku (resampling LANCZOS), konwersja do RGB.

## Szkic kodu

```python
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

pdf = pdfium.PdfDocument("skan.pdf")
for i, page in enumerate(pdf):
    pdfium_c.FPDFPage_Flatten(page, pdfium_c.FLAT_NORMALDISPLAY)
    w_pt = min(page.get_width(), page.get_height())
    scale_dpi = max((1024 / w_pt) * 72, 192)
    bitmap = page.render(scale=scale_dpi / 72)
    bitmap.to_pil().convert("RGB").save(f"strona_{i+1}.png")
```

Obraz idzie potem do VLM z szablonem `references/prompt_vlm_ocr_pl.md`,
a wyjscie do `normalize.py --engine vlm-html`.
