# S1: build with latexmk.  `make` builds main.pdf; `make watch` rebuilds on save;
# `make clean` removes auxiliaries; `make distclean` also removes the PDF.
MAIN := main
SRC  := $(MAIN).tex intro.tex prelims.tex q10.tex soundness.tex refs.bib

.PHONY: all watch clean distclean
all: $(MAIN).pdf

$(MAIN).pdf: $(SRC)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

clean:
	latexmk -c $(MAIN).tex
	command rm -f $(MAIN).bbl $(MAIN).run.xml

distclean: clean
	command rm -f $(MAIN).pdf
