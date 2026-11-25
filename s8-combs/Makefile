# S8: build with latexmk.  `make` builds main.pdf; `make watch` rebuilds on save;
# `make clean` removes auxiliaries; `make distclean` also removes the PDF.
MAIN := main
SRC  := $(MAIN).tex refs.bib fig/sasa.pdf fig/zs.pdf
GUARD := $(HOME)/Code/ski/notes/checks/s4/gcert/guard.sh 1000

.PHONY: all figs watch clean distclean
all: $(MAIN).pdf

$(MAIN).pdf: $(SRC)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

# Figures (each run a few seconds, under 100 MB; guarded at 1 GB).  Needs matplotlib and the S1
# tables in ~/Code/ski/notes/checks/s15/cert.
figs:
	cd fig && COMB=left ARGD=6 NLAB=8 FIGW=3.2 LABFS=8 $(GUARD) python3 spiral.py "S A S A" 20 sasa.pdf
	cd fig && COMB=first ARGD=5 SPINEF=0.9 TOOTHF=0.45 ALPHA=35 BETA=50 H0=20 NLAB=8 \
	  $(GUARD) python3 spiral.py "S T T (S T T) S" 16 zs.pdf

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

clean:
	latexmk -c $(MAIN).tex
	command rm -f $(MAIN).bbl $(MAIN).run.xml

distclean: clean
	command rm -f $(MAIN).pdf
