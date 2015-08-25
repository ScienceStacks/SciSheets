# Create compressed files to use for slickgrid
# Assumes that nodejs is installed and there is a link 
# from node to nodejs
# To run: make Makefile slickgrid

B=$(shell echo $(HOME))
DDIR=mysite/mysite/static
VERSION = $(shell python version.py)

N=$(B)/node_modules
SL=$(N)/slickgrid
SMASH=$(N)/.bin/smash
UGLIFYJS=$(N)/.bin/uglifyjs
UGLIFYCSS=/usr/local/bin/uglifycss

GENERATED_FILES = \
	$(DDIR)/slicklib.min.js \
	$(DDIR)/slicklib.js \
	$(DDIR)/slicklib.min.css

CSS_FILES = \
	$(SL)/css/smoothness/jquery-ui-1.8.16.custom.css \
	$(SL)/slick.grid.css \
	$(SL)/slick-default-theme.css \
	$(SL)/examples/examples.css \
	$(SL)/plugins/slick.headermenu.css \
	$(SL)/plugins/slick.headermenu.css

JS_FILES = \
	$(SL)/lib/jquery-1.7.min.js \
	$(SL)/lib/jquery.event.drag-2.0.min.js \
	$(SL)/lib/jquery-ui-1.8.16.custom.min.js \
	$(SL)/lib/firebugx.js \
	$(SL)/slick.groupitemmetadataprovider.js \
	$(SL)/plugins/slick.autotooltips.js \
	$(SL)/plugins/slick.cellcopymanager.js \
	$(SL)/plugins/slick.cellrangedecorator.js \
	$(SL)/plugins/slick.cellselectionmodel.js \
	$(SL)/plugins/slick.headermenu.js \
	$(SL)/slick.core.js \
	$(SL)/slick.dataview.js \
	$(SL)/slick.editors.js \
	$(SL)/slick.formatters.js \
	$(SL)/slick.grid.js

##################
# Rules
##################

.PHONY: target

slicklib: $(GENERATED_FILES) $(CSS_FILES) $(JS_FILES) package.json Makefile

$(DDIR)/slicklib.min.css: $(CSS_FILES) package.json
	$(SMASH) $(CSS_FILES) > $(DDIR)/slicklib.css
	$(UGLIFYCSS) $(DDIR)/slicklib.css > $@

$(DDIR)/slicklib.min.js: $(JS_FILES) package.json
	$(SMASH) $(JS_FILES) > $(DDIR)/slicklib.js
	$(UGLIFYJS) $(DDIR)/slicklib.js > $@

clean:
	@rm -f $(GENERATED_FILES)
