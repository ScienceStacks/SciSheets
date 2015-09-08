# Create compressed files to use for slickgrid
# Assumes that nodejs is installed and there is a link 
# from node to nodejs
# To run from the directory in which Makefile is present
#  make Makefile clean
#  make Makefile yui
# To re-acquire the source files used
#  make Makefile acquire

B=$(shell echo $(HOME))
CDIR=$(shell pwd)
DDIR=mysite/mysite/static

N=$(B)/node_modules
SL=$(N)/slickgrid
YUI=$(CDIR)/yui
YUI_JS=$(CDIR)/yui/js
YUI_CSS=$(CDIR)/yui/css
SMASH=$(N)/.bin/smash
UGLIFYJS=$(N)/.bin/uglifyjs
UGLIFYCSS=/usr/local/bin/uglifycss

JQUERY = $(DDIR)/jquery.min.js

SLICK_GENERATED_FILES = \
	$(DDIR)/slickgrid.min.js \
	$(DDIR)/slickgrid.js \
	$(DDIR)/slickgrid.min.css

SLICK_CSS_FILES = \
	$(SL)/css/smoothness/jquery-ui-1.8.16.custom.css \
	$(SL)/slick.grid.css \
	$(SL)/slick-default-theme.css \
	$(SL)/examples/examples.css \
	$(SL)/plugins/slick.headermenu.css \
	$(SL)/plugins/slick.headermenu.css

SLICK_JS_FILES = \
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

YUI_GENERATED_FILES = \
	$(DDIR)/yui.min.js \
	$(DDIR)/yui.js \
	$(DDIR)/yui.min.css

# Need to insert files in the order of the dependencies
YUI_CSS_FILES = \
	$(YUI_CSS)/reset.css \
	$(YUI_CSS)/fonts.css \
	$(YUI_CSS)/menu.css \
	$(YUI_CSS)/fonts-min.css \
	$(YUI_CSS)/calendar.css \
	$(YUI_CSS)/datatable.css

YUI_JS_FILES = \
	$(YUI_JS)/yahoo-dom-event.js \
	$(YUI_JS)/calendar-min.js \
	$(YUI_JS)/element-min.js \
	$(YUI_JS)/datasource-min.js \
	$(YUI_JS)/event-delegate-min.js \
	$(YUI_JS)/datatable-min.js \
	$(YUI_JS)/yahoo.js \
	$(YUI_JS)/event.js \
	$(YUI_JS)/dom.js \
	$(YUI_JS)/animation.js \
	$(YUI_JS)/container_core.js \
	$(YUI_JS)/menu.js

YUI_CSS_SRC = \
	http://yui.yahooapis.com/2.9.0/build/reset/reset.css \
	http://yui.yahooapis.com/2.9.0/build/fonts/fonts.css \
	http://yui.yahooapis.com/2.9.0/build/menu/assets/skins/sam/menu.css \
	http://yui.yahooapis.com/2.9.0/build/fonts/fonts-min.css \
	http://yui.yahooapis.com/2.9.0/build/calendar/assets/skins/sam/calendar.css \
	http://yui.yahooapis.com/2.9.0/build/datatable/assets/skins/sam/datatable.css

YUI_JS_SRC = \
	http://yui.yahooapis.com/2.9.0/build/yahoo/yahoo.js \
	http://yui.yahooapis.com/2.9.0/build/event/event.js \
	http://yui.yahooapis.com/2.9.0/build/dom/dom.js \
	http://yui.yahooapis.com/2.9.0/build/animation/animation.js \
	http://yui.yahooapis.com/2.9.0/build/container/container_core.js \
	http://yui.yahooapis.com/2.9.0/build/menu/menu.js \
	http://yui.yahooapis.com/2.9.0/build/yahoo-dom-event/yahoo-dom-event.js \
	http://yui.yahooapis.com/2.9.0/build/calendar/calendar-min.js \
	http://yui.yahooapis.com/2.9.0/build/element/element-min.js \
	http://yui.yahooapis.com/2.9.0/build/datasource/datasource-min.js \
	http://yui.yahooapis.com/2.9.0/build/event-delegate/event-delegate-min.js \
	http://yui.yahooapis.com/2.9.0/build/datatable/datatable-min.js

##################
# Rules
##################

clean:
	@rm -f $(SLICK_GENERATED_FILES)
	@rm -f $(YUI_GENERATED_FILES)
	@rm -f $(JQUERY)


############# SLICKGRID ####################

slickgrid: Makefile $(SLICK_GENERATED_FILES) $(SLICK_CSS_FILES) $(SLICK_JS_FILES) package.json $(JQUERY)

$(DDIR)/slickgrid.min.css: $(SLICK_CSS_FILES) package.json
	$(SMASH) $(SLICK_CSS_FILES) > $(DDIR)/slickgrid.css
	$(UGLIFYCSS) $(DDIR)/slickgrid.css > $@

$(DDIR)/slickgrid.min.js: $(SLICK_JS_FILES) package.json
	$(SMASH) $(SLICK_JS_FILES) > $(DDIR)/slickgrid.js
	$(UGLIFYJS) $(DDIR)/slickgrid.js > $@


############# YUI ####################
# Run the "yui" rule to obtain all YUI dependencies

yui: Makefile $(YUI_GENERATED_FILES) $(YUI_CSS_FILES) $(YUI_JS_FILES) package.json

$(DDIR)/yui.min.css: $(YUI_CSS_FILES) package.json
	$(SMASH) $(YUI_CSS_FILES) > $(DDIR)/yui.css
	$(UGLIFYCSS) $(DDIR)/yui.css > $@

$(DDIR)/yui.min.js: $(YUI_JS_FILES) package.json
	$(SMASH) $(YUI_JS_FILES) > $(DDIR)/yui.js
	$(UGLIFYJS) $(DDIR)/yui.js > $@


############# OTHER ####################

# The following rules are used to reacquire dependencies.
# The files themselves should already be in mysite/mysite/static
# The "dep" rule runs all of these
acquire: jquery_dep qunit_dep yui_dep

jquery_dep:
	@wget http://code.jquery.com/jquery-2.1.4.min.js
	@mv jquery-2.1.4.min.js $(JQUERY)

# Acquire the dependencies used for qunit
qunit_dep:
	@wget http://code.jquery.com/qunit/qunit-1.19.0.css
	@mv qunit-*.css $(DDIR)/qunit.css
	@wget http://code.jquery.com/qunit/qunit-1.19.0.js
	@mv qunit-*.js $(DDIR)/qunit.js

yui_dep:
	for ff in $(YUI_CSS_SRC); do \
	  wget $$ff; \
	done
	@mv *.css $(YUI_CSS)
#
	for ff in $(YUI_JS_SRC); do \
	  wget $$ff; \
	done
	@mv *.js $(YUI_JS)


.PHONY: clean acquire jquery_dep qunit_dep yui_dep
