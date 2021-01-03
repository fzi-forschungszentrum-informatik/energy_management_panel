(function($) {
    $(function() {

   

        function toggleInline(obj) {
            var value = obj.val();
            var count = parseInt(obj.attr('id').match(/\d+/)[0])
            var uielement = $('#pageelement_set-' + count + '-uielement_set-group');
            var uielementcontainer = $('#pageelement_set-' + count + '-uielementcontainer_set-group');

            if (value === 'container') {
                uielementcontainer.show();
                uielement.hide();
            } else if (value === "element") {
                uielementcontainer.hide();
                uielement.show();
            }
            else {
                uielementcontainer.hide();
                uielement.hide();
            }
        }
        
        function toggleInlineInAllSets() {
            $('[id^=id_pageelement_set][id$=element_type]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=element_type]').length-1) {
                    return;
                }
                toggleInline($(value));
            });
        }
       
        
        // show/hide on change
        $('[id^=id_pageelement_set][id$=element_type]').change(function() {
            toggleInline($(this));
        });

        $(".add-handler").click(function() {
            setTimeout(() => {  toggleInlineInAllSets() }, 100);
            
        });

        
    });
})(django.jQuery);