# S8: build with latexmk.  `make` builds main.pdf; `make watch` rebuilds on save;
# `make clean` removes auxiliaries; `make distclean` also removes the PDF.
MAIN := main
FIGS := fig/02-teeth.pdf fig/05-theta.pdf fig/09-threehole.pdf
SRC  := $(MAIN).tex refs.bib $(FIGS)
GUARD := $(HOME)/Code/ski/notes/checks/s4/gcert/guard.sh 1000

.PHONY: all figs watch clean distclean
all: $(MAIN).pdf

$(MAIN).pdf: $(SRC)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

# Figures (a few seconds each; guarded at 1 GB).  Needs matplotlib.  The script builds the tree
# from the context alone; no term is reduced.
figs:
	cd fig && N='S S' $(GUARD) python3 -I forbidden.py 'S n p' 18 02-teeth.pdf
	cd fig && N='S' ALPHA=75 BETA=55 $(GUARD) python3 -I forbidden.py 'S p p' 14 05-theta.pdf
	cd fig && N='S S' ALPHA=75 BETA=55 $(GUARD) python3 -I forbidden.py 'S (S p p) (S n p)' 14 09-threehole.pdf

watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

clean:
	latexmk -c $(MAIN).tex
	command rm -f $(MAIN).bbl $(MAIN).run.xml

distclean: clean
	command rm -f $(MAIN).pdf
