# S9: build with latexmk.  `make` builds main.pdf; `make watch` rebuilds on save;
# `make clean` removes auxiliaries; `make distclean` also removes the PDF.
MAIN := main
SRC  := $(MAIN).tex refs.bib fig/graph.pdf
GUARD := $(shell command -v guard.sh 2>/dev/null || echo $(HOME)/Code/ski/notes/checks/s4/gcert/guard.sh) 1000

.PHONY: all figs watch clean distclean
all: $(MAIN).pdf

$(MAIN).pdf: $(SRC)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

# Figure (a second, under 100 MB; guarded at 1 GB).  Needs matplotlib and the S1 tables in
# fig/s1table.json (the S1 table).  The script asserts the table facts of Lemma 8.
figs:
	cd fig && $(GUARD) python3 -I graph.py graph.pdf

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

clean:
	latexmk -c $(MAIN).tex
	command rm -f $(MAIN).bbl $(MAIN).run.xml

distclean: clean
	command rm -f $(MAIN).pdf
