/*
 Initialize the ContextMenu instance when the the elements 
 that trigger their display are ready to be scripted.
*/

YAHOO.util.Event.onContentReady("dataset", function () {

				var Dom = YAHOO.util.Dom;

    /*
        Map of CSS class names to arrays of MenuItem 
        configuration properties.
    */

    var oContextMenuItems = {
    
        "type1": [
                    "Context Menu 1, Item 1", 
                    {
                        text: "Context Menu 1, Item 2", 
                        submenu: { 
                                    id: "submenu1", 
                                    lazyload: true, 
                                    itemdata: [
                                        "Context Menu 1 Submenu, Item 1", 
                                        "Context Menu 1 Submenu, Item 2", 
                                        "Context Menu 1 Submenu, Item 3", 
                                        "Context Menu 1 Submenu, Item 4"
                                    ] 
                                } 
                    }, 
                    "Context Menu 1, Item 3", 
                    "Context Menu 1, Item 4"
                ],

        "type2": [
                    "Context Menu 2, Item 1", 
                    "Context Menu 2, Item 2", 
                    "Context Menu 2, Item 3", 
                    "Context Menu 2, Item 4", 
                    "Context Menu 2, Item 5", 
                    "Context Menu 2, Item 6", 
                    "Context Menu 2, Item 7", 
                    "Context Menu 2, Item 8", 
                    "Context Menu 2, Item 9", 
                    "Context Menu 2, Item 10"
                ],

        "type3": [
                    "Context Menu 3, Item 1", 
                    "Context Menu 3, Item 2", 
                    "Context Menu 3, Item 3", 
                    "Context Menu 3, Item 4"
                ],

        "type4": [
                    "Context Menu 4, Item 1", 
                    "Context Menu 4, Item 2"
                ],

        "type5": [
                    "Context Menu 5, Item 1", 
                    "Context Menu 5, Item 2", 
                    "Context Menu 5, Item 3", 
                    "Context Menu 5, Item 4", 
                    "Context Menu 5, Item 5", 
                    "Context Menu 5, Item 6"
                ]
    
    };

    var oSelectedTR,  // The currently selected TR
        rendered;     // Whether or not the menu has been rendered

    /*
         "triggerContextMenu" event handler for the ContextMenu instance - 
         replaces the content of the ContextMenu instance based 
         on the CSS class name of the <tr> element that triggered
         its display.
    */

    function onTriggerContextMenu(p_sType, p_aArgs) {

        var oTarget = this.contextEventTarget,
        	aMenuItems,
            aClasses;


        if (this.getRoot() == this) {

            /*
                 Get the <tr> that was the target of the 
                 "contextmenu" event.
            */
       
						oSelectedTR = oTarget.nodeName.toUpperCase() == "TR" ? 
										oTarget : Dom.getAncestorByTagName(oTarget, "TR");
   
   
            /*
                Get the array of MenuItems for the CSS class name from 
                the "oContextMenuItems" map.
            */
   
            if (Dom.hasClass(oSelectedTR, "odd")) {
                aClasses = oSelectedTR.className.split(" ");
                aMenuItems = oContextMenuItems[aClasses[0]];
            } else {
                aMenuItems = oContextMenuItems[YAHOO.lang.trim(oSelectedTR.className)];
            }
   
            // Remove the existing content from the ContentMenu instance
            this.clearContent();
   
            // Add the new set of items to the ContentMenu instance                    
            this.addItems(aMenuItems);

            // Render the ContextMenu instance with the new content
            if (!rendered) {
                this.render(this.cfg.getProperty("container"));
            } else {
                this.render();
            }

            /*
                 Highlight the <tr> element in the table that was 
                 the target of the "contextmenu" event.
            */
            Dom.addClass(oSelectedTR, "selected");
        }
    }

    /*
         "hide" event handler for the ContextMenu - used to 
         clear the selected <tr> element in the table.
    */
    function onContextMenuHide(p_sType, p_aArgs) {
        if (this.getRoot() == this && oSelectedTR) {
            Dom.removeClass(oSelectedTR, "selected");
        }
    }

    /*
      Instantiate a ContextMenu:  The first argument passed to the constructor
      is the id for the Menu element to be created, the second is an 
      object literal of configuration properties.
    */

    var oContextMenu = new YAHOO.widget.ContextMenu("contextmenu", { 
            trigger: "dataset", 
            lazyload: true 
    });
    

    /*
     Subscribe to the ContextMenu instance's "triggerContextMenu" event to update content, 
     and "hide" event to clear the selected row state.
    */
    oContextMenu.subscribe("triggerContextMenu", onTriggerContextMenu);
    oContextMenu.subscribe("hide", onContextMenuHide);
    oContextMenu.subscribe("render", function() {rendered = true;});
});
