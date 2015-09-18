$( "#menu" ).menu(

{       role: "listbox",

        select: function( event, data ) {
            var thisEle = event.currentTarget;
            var thisEleId = event.currentTarget.id;
            var myData = data;
            alert( "Selected " + thisEleId);
        }
}
);
