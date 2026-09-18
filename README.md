# ELE456 lecture notes

[Download the lecture notes (PDF)](main.pdf)

## License and preparation

Copyright © 2026 Paolo Stegagno, to the extent copyright applies.
Unless otherwise noted, the notes, diagrams, and their LaTeX/TikZ sources are
licensed under [Creative Commons Attribution-NonCommercial 4.0 International
(CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).
You may share and adapt the material for noncommercial purposes with appropriate
attribution, a link to the license, and an indication of changes. Commercial
uses outside the license require separate permission from Paolo Stegagno.
See [LICENSE](LICENSE) for the full terms. The license does not restrict uses
that are otherwise permitted by law or material in the public domain.

Suggested attribution: Paolo Stegagno, *ELE456 Lecture Notes*, 2026,
CC BY-NC 4.0. Include a link to this repository when redistributing the notes.

These notes are prepared with AI assistance from Paolo Stegagno's lecture
transcripts and board material and reviewed by the instructor. Errors may
remain; please report suspected mistakes to help improve the notes.

## Contents

One LaTeX chapter per class. The first chapter combines the September 10, 2026
board image and transcript into a textbook-style chapter titled
"Introduction and linear algebra," with definitions and worked matrix examples.
Course logistics and recording references are excluded from the student notes.
Chapter 2, "Reference frames and planar rotations," develops coordinate
transformations with six editable TikZ figures and an additional exercise page.
Chapter 3, "Planar rigid transformations and homogeneous coordinates," adds
translation, homogeneous matrices, composition, and inversion, with four TikZ
figures and a page of exercises.

## Build

From this folder, run:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The second pass resolves the table of contents and cross-references. The output
is `main.pdf`. A TeX distribution such as MiKTeX or TeX Live is required.
Alternatively, use `latexmk -pdf main.tex` if latexmk and its dependencies are installed.
On Overleaf, upload the project and select `main.tex` as the main document.

## Organization

- `main.tex`: title, contents, and chapter inclusion order.
- `preamble.tex`: shared formatting, packages, and notation.
- `chapters/lecture01.tex`: first lecture notes.
- `chapters/lecture02.tex`: second lecture notes.
- `chapters/lecture03.tex`: third lecture notes.
- `figures/lecture02/`: vector diagrams drawn in TikZ and included by the chapter.
- `figures/lecture03/`: diagrams for affine and homogeneous transformations.
- `chapters/lecture-template.tex`: starting point for future lectures.
- `lectures/01/`, `02/`, `03/`: original boards and transcripts, preserved unchanged.
- `editorial-notes.md`: source decisions and details requiring confirmation.

## Add a lecture

1. Put its board material and transcript in `lectures/04/`, then `05/`, etc.
2. Copy `chapters/lecture-template.tex` to `chapters/lecture04.tex`.
3. Set a descriptive chapter title and unique labels, and write the notes.
4. Add `\input{chapters/lecture04}` after the third chapter in `main.tex`.
5. Build twice. Chapter, section, and equation numbering update automatically.

Use board images to resolve spoken matrix entries and the transcript to explain
the reasoning. Correct clear transcription errors, preserve the scope of the
lecture, and record unresolved ambiguities in `editorial-notes.md` rather than
inventing details. Write directly about the subject, without references to the
board, recording, or classroom discussion. Keep syllabus material and software
setup logistics out of the chapters.

Figures use TikZ (the PGF package), compiled directly by pdfLaTeX. They need
no external graphics editor or image conversion. World axes are black, robot
axes red, and sensor axes blue; every axis is also labeled explicitly.
