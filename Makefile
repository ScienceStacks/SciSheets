# Manage dependencies on yui, jquery, jquery-ui, jquery-mockjax, qunit
# Assumes 
#  -nodejs is installed
#  -there is a link from node to nodejs
#  -running from the directory of the Makefile
# To run:
#  make Makefile clean
#  make Makefile yui
# To re-acquire the source files used
#  make Makefile acquire
# Issues
#  1. Broken
#  2. Do I need to compile the components of the API if I can download
#     a built API for YUI?

B=$(shell echo $(HOME))
CDIR=$(shell pwd)
DDIR=mysite/mysite/static
DDIR_YUI=$(DDIR)/yui
DDIR_JQUERY=$(DDIR)/jquery
DDIR_JQUERYUI=$(DDIR)/jquery-ui
DDIR_JQUERYLINEDTEXTAREA=$(DDIR)/jquery-linedtextarea
DDIR_JQUERYMOCKJAX=$(DDIR)/jquery_mockjax
DDIR_QUNIT=$(DDIR)/qunit

N=$(B)/node_modules
YUI=$(CDIR)/yui
YUI_JS=$(CDIR)/yui/js
YUI_API=yuiapi.min.js
YUI_CSS=$(CDIR)/yui/css
SMASH=$(N)/.bin/smash
UGLIFYJS=$(N)/.bin/uglifyjs
UGLIFYCSS=/usr/local/bin/uglifycss

JQUERY = $(DDIR_JQUERYUI)/jquery.min.js

YUI_GENERATED_FILES = \
	$(DDIR_YUI)/yui.min.js \
	$(DDIR_YUI)/yui.js \
	$(DDIR_YUI)/yui.min.css

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
	@rm -f $(YUI_GENERATED_FILES)
	@rm -f $(DDIR_JQUERY)/*.*
	@rm -f $(DDIR_JQUERYUI)/*.*
	@rm -f $(DDIR_JQUERYLINEDTEXTAREA)/*.*

# TODO: Add jquery-ui
all: yui jquery jquery-linedtextarea


############# YUI ####################
# Run the "yui" rule to obtain all YUI dependencies

yui: Makefile $(DDIR_YUI)/yui.min.css $(DDIR_YUI)/yui.min.js package.json $(DDIR_YUI)/$(YUI_API)

$(DDIR_YUI)/yui.min.css: $(YUI_CSS_FILES) package.json
	$(SMASH) $(YUI_CSS_FILES) > $(DDIR_YUI)/yui.css
	$(UGLIFYCSS) $(DDIR_YUI)/yui.css > $@

$(DDIR_YUI)/yui.min.js: $(YUI_JS_FILES) package.json
	$(SMASH) $(YUI_JS_FILES) > $(DDIR_YUI)/yui.js
	$(UGLIFYJS) $(DDIR_YUI)/yui.js > $@

$(DDIR_YUI)/$(YUI_API):
	@mkdir -p $(DDIR_YUI)
	@wget http://yui.yahooapis.com/3.18.1/build/yui/yui-min.js -O $(YUI_API)
	@rm -f $(DDIR_JQUERY)/$(YUI_API)
	@mv $(YUI_API) $(DDIR_JQUERY)/


############# OTHER ####################

# The following rules are used to reacquire dependencies.
# The files themselves should already be in mysite/mysite/static
# The "dep" rule runs all of these
acquire: jquery qunit yui_dep jquery_mockjax

jquery_mockjax:
	cp jquery-mockjax/src/jquery.mockjax.js $(DDIR_JQUERYMOCKJAX)/jquery_mockjax

jquery:
	@mkdir -p $(DDIR_JQUERY)
	@wget http://code.jquery.com/jquery-2.1.4.min.js
	@mv jquery-2.1.4.min.js $(DDIR_JQUERY)/jquery.min.js

# Bad files in git repo
jquery-linedtextarea:
	#j@wget https://github.com/cotenoni/jquery-linedtextarea/blob/master/jquery-linedtextarea.css
	#@wget https://github.com/cotenoni/jquery-linedtextarea/blob/master/jquery-linedtextarea.js
	#@mv jquery-linedtextarea.* $(DDIR_JQUERYLINEDTEXTAREA)

# Acquire the dependencies used for qunit
qunit:
	@wget http://code.jquery.com/qunit/qunit-1.19.0.css
	@mv qunit-*.css $(DDIR_QUNIT)/qunit.css
	@wget http://code.jquery.com/qunit/qunit-1.19.0.js
	@mv qunit-*.js $(DDIR_QUNIT)/qunit.js

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


.PHONY: clean acquire jquery_dep qunit_dep yui_dep jquery_mockjax_dep
