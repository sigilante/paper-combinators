# Build every child project (any subdirectory with its own Makefile).
#   make            build all children
#   make s2-productive-terms   build one child
#   make clean      latexmk -c in every child
#   make distclean  also remove PDFs
SUBDIRS := $(patsubst %/Makefile,%,$(wildcard */Makefile))

.PHONY: all clean distclean $(SUBDIRS)
all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean distclean:
	@for d in $(SUBDIRS); do $(MAKE) -C $$d $@ || exit 1; done
