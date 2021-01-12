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


        function initOnAddHandler() {
            toggleInlineInAllSets();
            container_has_title_toggle_all();
            presentation_inline_toggle_all();
            card_has_tooltip_toggle_all();
            card_is_button_toggle_all();
            chart_has_title_toggle_all();
            container_has_dropdown_toggle_all();
        }

        $(".add-handler").click(function() {
            setTimeout(() => {  initOnAddHandler() }, 100);          
        });

        function container_has_title_toggle(obj) {
            var checked = obj.is(":checked");
            var titleField = $('#' + obj.attr('id').split("has_title")[0].concat("title"))
            if (checked) {
                titleField.parent().parent().show();
            }
            else {
                titleField.parent().parent().hide();
            }

        }

        // show/hide on change
        $('[id^=id_pageelement_set][id$=container_has_title]').change(function() {
            container_has_title_toggle($(this));
        });

        function container_has_title_toggle_all() {
            $('[id^=id_pageelement_set][id$=container_has_title]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=container_has_title]').length-1) {
                    return;
                }
                container_has_title_toggle($(value));
            });
        }

        function container_has_dropdown_toggle(obj) {
            var checked = obj.is(":checked");
            var titleField = $('#' + obj.attr('id').split("container_has_dropdown")[0].concat("container_dropdown_links"))
            if (checked) {
                titleField.parent().parent().show();
            }
            else {
                titleField.parent().parent().hide();
            }

        }

        // show/hide on change
        $('[id^=id_pageelement_set][id$=container_has_dropdown]').change(function() {
            container_has_dropdown_toggle($(this));
        });

        function container_has_dropdown_toggle_all() {
            $('[id^=id_pageelement_set][id$=container_has_dropdown]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=container_has_dropdown]').length-1) {
                    return;
                }
                container_has_dropdown_toggle($(value));
            });
        }

        function presentation_inline_toggle(obj) {
            var value = obj.val();
            var elementStub = obj.attr('id').split("id_")[1].split("presentation_type")[0];
            var cardElement = $('#' + elementStub + 'card_set-group');
            var chartElement = $('#' + elementStub + 'chart_set-group');

            if (value === 'card') {
                cardElement.show();
                chartElement.hide();
            } else if (value === "chart") {
                cardElement.hide();
                chartElement.show();
            }
            else {
                cardElement.hide();
                chartElement.hide();
            }
        }

        $('[id^=id_pageelement_set][id$=presentation_type]').change(function() {
            presentation_inline_toggle($(this));
        });

        function presentation_inline_toggle_all() {
            $('[id^=id_pageelement_set][id$=presentation_type]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=presentation_type]').length-1) {
                    return;
                }
                presentation_inline_toggle($(value));
            });
        }

        function card_has_tooltip_toggle(obj) {
            var checked = obj.is(":checked");
            var textField = $('#' + obj.attr('id').split("has_tooltip")[0].concat("tooltip_text"))
            if (checked) {
                textField.parent().parent().show();
            }
            else {
                textField.parent().parent().hide();
            }

        }

        // show/hide on change
        $('[id^=id_pageelement_set][id$=card_has_tooltip]').change(function() {
            card_has_tooltip_toggle($(this));
        });

        function card_has_tooltip_toggle_all() {
            $('[id^=id_pageelement_set][id$=card_has_tooltip]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=card_has_tooltip]').length-1) {
                    return;
                }
                card_has_tooltip_toggle($(value));
            });
        }

        function card_is_button_toggle(obj) {
            var checked = obj.is(":checked");
            var textField = $('#' + obj.attr('id').split("card_is_button")[0].concat("card_button_link"))
            if (checked) {
                textField.parent().parent().parent().show();
            }
            else {
                textField.parent().parent().parent().hide();
            }

        }

        // show/hide on change
        $('[id^=id_pageelement_set][id$=card_is_button]').change(function() {
            card_is_button_toggle($(this));
        });

        function card_is_button_toggle_all() {
            $('[id^=id_pageelement_set][id$=card_is_button]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=card_is_button]').length-1) {
                    return;
                }
                card_is_button_toggle($(value));
            });
        }

        function chart_has_title_toggle(obj) {
            var checked = obj.is(":checked");
            var textField = $('#' + obj.attr('id').split("chart_has_title")[0].concat("chart_title"))
            if (checked) {
                textField.parent().parent().show();
            }
            else {
                textField.parent().parent().hide();
            }

        }

        // show/hide on change
        $('[id^=id_pageelement_set][id$=chart_has_title]').change(function() {
            chart_has_title_toggle($(this));
        });

        function chart_has_title_toggle_all() {
            $('[id^=id_pageelement_set][id$=chart_has_title]').each( function(index, value){
                if(index === $('[id^=id_pageelement_set][id$=chart_has_title]').length-1) {
                    return;
                }
                chart_has_title_toggle($(value));
            });
        }

        initOnAddHandler()
    });
})(django.jQuery);