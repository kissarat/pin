$(document).ready(function() {
    function getMeta(url) {
        var img = new Image();
        img.src = url;
        img.onerror = function() {
            gallery.loadError();
        };
        img.onload = function() {
            gallery.setdata({
                url: url,
                w: this.width,
                h: this.height
            });
        }
    }
    $( "#dialog-form" ).dialog({
	        autoOpen: false,
	        height: 250,
	        width: 450,
	        modal: true,
	        show: {
                effect: "clip",
                duration: 200
              }
	        });
	$( "#getlist-from-web" ).dialog({
	        autoOpen: false,
	        height: 200,
	        width: 450,
	        modal: true,
	        show: {
                effect: "clip",
                duration: 200
              }
	        });
    $("#web_getlist_link").click(function(){
        $( "#getlist-from-web" ).dialog( "open" );
    });
    $(".add_getlist_link").click(function(){
        $( "#dialog-form" ).dialog( "open" );
        return false;
    });

    $("#upload_cancel").click(function(){
        $( "#dialog-form" ).dialog( "close" );
    });

    $("#get_cancel").click(function(){
        $( "#getlist-from-web" ).dialog( "close" );
    });

    $( "#addpindialogform" ).dialog({
	        autoOpen: false,
	        height:650,
	        width: 700,
	        modal: true
	        });
	$( "#addpindialogformweb" ).dialog({
	        autoOpen: false,
	        height:700,
	        width: 800,
	        modal: true
	        });
    function validate(){
        if ($("#image").val())
            return true;
        else {
            $("#status").html("please choose a file");
            return false;
        }
    }
    var bar = $('.bar');
    var percent = $('.percent');

    $('#upload_form').ajaxForm({
        beforeSend: function(xhr, opts) {
            $(".loading").show();
            if (validate())
                return true;
            xhr.abort();
        },

        success: function() {
            $(".loading").show();
        },

	    complete: function(xhr) {
	       $(".progress").hide();
	        $( "#dialog-form" ).clearForm();
	        var percentVal = '0%';
            bar.width(percentVal);
            percent.html(percentVal);
            var obj = jQuery.parseJSON( xhr.responseText );
            $("#fname").val(obj.fname);
            $("#imagename").html(obj.original_filename);
	        $( "#dialog-form" ).dialog("close");
	        //$("#imagediv").html('<img src="/'+obj.fname+'" alt="">')
	        loadImage('/'+obj.fname, $("#slideshowupload"));
		    $( "#addpindialogform" ).dialog("open");
		    $("#comments").focus();
	    }
    });

    function loadImage(url, element){
        var img = new Image();
        img.src = url;
        img.id = "uploadimage";
        img.onerror = function() {
            alert('error in load');
        };
        img.onload = function() {
            element.empty()
                .append(img);
            $("#uploadimage").attr("class", this.width > this.height
                ? "img-width" : "img-height");
        }
    }

    $("#gallerynextweb").click(function() {
        gallery.next();
    });

    $("#galleryprevweb").click(function() {
        gallery.prev();
    });

    function show_fetch_images_error(error) {
        $("#statusweb").html(error);
        $(".block-loading").hide();
        $("#getlist-from-web").dialog("open");
        return false;
    }

    function fetch_images() {
        var url_input_to_fetch = $('#url');
        if (!url_input_to_fetch.val())
            url_input_to_fetch = $('#url-in-profile');

        var url = url_input_to_fetch.val();
        url_input_to_fetch.val('');
        if (is_image_url(url))
            initgallery([url]);
        else {
            function abort_preview(e) {
                if (KeyCodes.ESC != e.keyCode)
                    return;
                request.abort();
                request = null;
            }

            var request = $.ajax({
                url: "/preview",
                dataType: 'json',
                timeout: 80000,
                cache: true,
                data: { url: url },

                beforeSend: function() {
                    $("#getlist-from-web").dialog("close");
                    $(window).keyup(abort_preview);
                    $(".block-loading").show();
                },

                success: function(data) {
                    if ('error' == data.status)
                        return show_fetch_images_error(data.error);
//                $("#statusweb").html("please provide a valid image url");
                    if (1 != data.images.length)
                        $("#websitelinkweb").val(url);
                    if (!$('#titleweb').val())
                        $('#titleweb').val(data.title);
                    $("#getlist-from-web").clearForm();
                    $(".block-loading").hide();
                    $("#addpindialogformweb").dialog("open");
                    initgallery(data.images);
                },

                error: function(xhr, status, error) {
                    show_fetch_images_error(error);
                },

                complete: function(xhr, status) {
                    $(window).unbind('keyup', abort_preview);
                    console.log('preview ' + status + ' ' + url);
                    //show_fetch_images_error(status);
                }
            });
        }
    }

    $('#fetch-images, #fetch-images-profile').click(fetch_images);
    $('#web_getlist_form').submit(function(e) {
        e.preventDefault();
        fetch_images();
    });

    function initgallery(data){
        gallery.lengthTotal = data.length;
        if (1 == gallery.lengthTotal)
            $('#controls-web').hide();
        else
            $('#controls-web').show();
        gallery.data = [];
        for(var i=0; i<data.length; i++){
            getMeta(data[i]);
        }

        //gallery.init();
    }

    function getdata() {
        return {
            title:    $("#title").val(),
            weblink:  $("#weblink").val(),
            lists:    $("#board").val(),
            comments: $("#comments").val(),
            fname:    $("#fname").val(),
            hashtags: $("#hashtag").val()
        };
    }

    function getdataweb() {
        return {
            title:      $("#titleweb").val(),
            link:       $("#weblinkweb").val(),
            description:$("#commentsweb").val(),
            image_url:  $("#image_urlweb").val(),
            list:       $("#boardweb").val(),
            price:      $("input:radio[name='price_range']:checked").val() || '',
            websiteurl: $("#websitelinkweb").val(),
            board_name: '',
            hashtags:   $("#hashtagweb").val()
        };
    }

    function successcall(data){
        //$( "#addpindialogform" ).dialog("close");
        $(location).attr('href',data);
    }

    $('#cancelfancy').click(function(){
        $( "#addpindialogform" ).dialog("close");
    });

    $('#cancelfancyweb').click(function(){
        $( "#addpindialogformweb" ).dialog("close");
    });


    $('#ajaxpinform').submit(function() {
        // submit the form
        $(this).ajaxSubmit({
            beforeSubmit: validate_from_upload,
            data:getdata(),
            success: successcall
        });
        // return false to prevent normal browser submit and page navigation
        return false;
    });

    $('#ajaxpinformweb').submit(function() {
        // submit the form
        $(this).ajaxSubmit({
            beforeSubmit: validate_from_web,
            data:getdataweb(),
            success: successcall
        });
        // return false to prevent normal browser submit and page navigation
        return false;
    });

    function validate_from_upload(formData, jqForm, options) {
        var title = $("#title");
        var weblink = $("#weblink");
        var list = $("#board");

        var errors = [];
        if(!title.val())
            errors.push(title);
        else
            title.removeAttr("style");

        if(!weblink.val())
            errors.push(weblink);
        else
            weblink.removeAttr("style");

        if(!list.val())
            errors.push(list);
        else
            list.removeAttr("style");

        if (errors.length>0){
            $("body").removeClass("loading");
            for (var i=0 ;i<errors.length; i++) {
                if (errors[i] instanceof jQuery)
                    $.each(errors[i], function(_, v) {
                        $(v).attr("style", "outline:1px solid red;");
                    });
                else
                    errors[i].attr("style", "border:1px solid red;");
            }
            return false;
        }
        $("#addfancy").prop("disabled", true);
        var spanelememnt = $("#addtogetlistupload");
        spanelememnt.empty();
        $("body").addClass("loading");
        // spanelememnt.append("<img src='/static/img/getlist-load.gif'>")
        return true;
    }

    function validate_from_web(formData, jqForm, options) {
        var title = $("#titleweb");
        var list = $("#boardweb");

        var errors = [];
        if(!title.val())
            errors.push(title);
        else
            title.removeAttr("style");

        if(!list.val())
            errors.push(list);
        else
            list.removeAttr("style");

        for (var i in errors) {
            if(errors[i] instanceof jQuery)
                $.each(errors[i], function(_, v) {
                    $(v).attr("style", "outline:1px solid red;");
                });
            else
                errors[i].attr("style", "border:1px solid red;");
        }
        if (errors.length>0)
            return false;

        $("#addfancyweb").prop("disabled", true);
        var spanelememnt = $("#addtogetlist");
        spanelememnt.empty();
        $("body").addClass("loading");
        // spanelememnt.append("<img src='/static/img/getlist-load.gif'>")
        return true;
    }

    var gallery = {
        data: [],
        element: $("#slide-imageweb"),
        show: function() {
            if(0 == this.lengthTotal) {
                this.len = this.data.length;
                $(".block-loading").hide();
                $( "#addpindialogformweb" ).dialog("open");
                $("#commentsweb").focus();
                this.init();
                this.showitem();
            }
        },
        setdata: function(data){
            this.lengthTotal--;
            if(data.w * data.h > 200*200)
                this.data.push(data);
            this.show();
        },
        loadError: function(){
            this.lengthTotal--;
            this.show();
        },
        next: function(){
            if (this.current < this.len-1)
                this.current++;
            this.showitem();
        },
        prev: function(){
            if (this.current > 0)
                this.current--;
            this.showitem();
        },
        showitem : function(){
            var current = this.data[this.current];
            this.element.attr("src", current.url);
            if(current.w > current.h){
                this.element.attr("class", "img-width");
            }else{
                this.element.attr("class", "img-height");
            }
            $("#image_urlweb").val(current.url);
            this.showstatus();
            this.showsize();
        },
        showstatus : function(){
            $("#status-textweb").html("   "+(this.current+1) + " of "+this.len);
        },
        showsize: function(){
            var elem = $("#imagesize");
            elem.empty();
            $('<span/>')
                .html(this.data[this.current].w + ' x ' + this.data[this.current].h)
                .appendTo(elem);
        },
        init: function(){
            this.element = $("#slide-imageweb");
            this.current = 0;
            this.element.removeAttr("src");
        }
    };

    $('#button_add_board').click(function(event) {
    	event.preventDefault();
    	$('#board').val('');
    	$('#board_selection_layer').hide();
    	$('#board_creation_layer').show();
    });

    $('#button_select_board').click(function(event) {
    	event.preventDefault();
    	$('#board_name').val('');
    	$('#board_creation_layer').hide();
    	$('#board_selection_layer').show();
    });

    $('#button_add_boardweb').click(function(event) {
        event.preventDefault();
        $('#board').val('');
        $('#board_selection_layerweb').hide();
        $('#board_creation_layerweb').show();
    });

    $('#button_select_boardweb').click(function(event) {
        event.preventDefault();
        $('#board_name').val('');
        $('#board_creation_layerweb').hide();
        $('#board_selection_layerweb').show();
    });

    $('#tabs').tabs();

    var suggestion_services = [];
    var suggestion_query = '';

    function request_suggestion(q) {
        for(var service; service = suggestion_services.pop();)
            service.abort();
        $('#suggestions').empty();

        //Users name request
        if (q.match(/^\w+$/) || 'last' == q)
            suggestion_services.push($.getJSON('/api/search/suggest?q=' + ('last' != q ? q : ''),
                function(names) {
                    for(var i in names) {
                        var name = names[i];
                        var $option = $('<option/>');
                        if ('string' == typeof name)
                            $option.val(name);
                        else
                            $option
                                .val(name[0])
                                .html(name[1]);
                        $option.appendTo('#suggestions');
                    }
                }));

        //Google suggestions request
        /*suggestion_services.push($.ajax({
            url:'http://suggestqueries.google.com/complete/search?' +
                'client=firefox&output=jsonp&jsonp=suggest&q=' + q,
            dataType: 'jsonp',
            jsonp: false
        }));*/
    }

    function last_suggestions() {
            if (0 == $('#suggestions option').length && !$('[list=suggestions]').val())
                request_suggestion('last');
        }

    var keyup_timeout_id;
    $('[list=suggestions]')
        .keyup(function() {
            var q = this.value;
            q = $.trim(q);
            q = q.replace(/ +/g, ' ');
            if (!q || suggestion_query == q)
                return;
            suggestion_query = q;
            clearTimeout(keyup_timeout_id);
            keyup_timeout_id = setTimeout(request_suggestion.bind(this, q), 200);
        })
        .click(last_suggestions);
});

//Google suggestions callback
/*function suggest(values) {
    values = values[1];
    for(var i in values)
        $('<option/>').val(values[i]).appendTo('#suggestions');
}*/

/* ----- Images web search ----- */
function load_image_from_url(image, url, title) {
    $('#url').val(image);
    $("#websitelinkweb").val(url);
    $('#titleweb').val(title);
    //$('#web_getlist_link').click();
    $('#fetch-images').click();
}

function is_image_url(url) {
    return /(\.jpg|\.jpeg|\.png|\.gif|\.bmp)$/.test(url);
}

var websearch = {
    offset: 0,
    buffer: [],
    length: 0,
    count: 12,

    addImages: function(results) {
        var row;
        for(var i = 0, result;
            $('#search_results img').length < websearch.length
                && (result = results.shift());
                i++) {
            if (i%4 == 0)
                row = $('<div></div>').appendTo('#search_results');
            while (result.image != decodeURIComponent(result.image))
                result.image = decodeURIComponent(result.image);
            var thumb = $('<img/>')
                .attr('src', result.thumb)
                .attr('data-src', result.image)
                .load(function() {
//                    if (!is_image_url(this.getAttribute('data-src')))
//                        return;
                    var img = new Image();
                    var self = $(this);
                    img.onload = function() {
                        self.attr('src', this.src);
                        self.unbind('load');
                    };
                    img.src = self.attr('data-src');
                    self.removeAttr('data-src');
                    /*img.onerror = function() {
                        self.src = '/static/img/unavailable.png';
                        $(self.parentNode)
                            .addClass('unavailable')
                            .off('click');
                    };*/
                });
            $('<div></div>')
                .append(thumb)
                .append($('<div></div>').html(result.title))
                .append($('<div></div>').html(result.desc))
                .click(load_image_from_url.bind(this,
                    result.image,
                    result.url,
                    decodeHTMLEntities(result.title)))
                .appendTo(row);
            websearch.offset++;
        }
        return websearch.offset < websearch.length;
    },

    loadImages: function() {
        websearch.length = websearch.offset + websearch.count;
        if (websearch.addImages(websearch.buffer))
                websearch.request();
    },

    request: function() {
        $.getJSON('/api/websearch/images?q=' + query + '&offset=' + websearch.offset,
            function(results) {
                if (websearch.addImages(results))
                    websearch.request();
                else
                    websearch.buffer = results;
            });
    }
};

function inverse(obj) {
	var result = {};
	for(var key in obj) result[obj[key]] = key;
	return result;
}

function decodeHTMLEntities(str) {
    if (!str) {
        console.error('Invalid string for decodeHTMLEntities');
        return '';
    }

	str = str.replace(/(&#\d+;)/g, function(entity) {
		entity = entity.slice(2, -1);
		entity = parseInt(entity);
		if (entity < 0 || entity >= 65536) {
			console.error('HTML entity code is out of range ' + entity);
			return '';
		}
		return String.fromCharCode(entity);
	});
	str = str.replace(/(&\w+;)/g, function(entity) {
		entity = entity.slice(1, -1);
		var entityCode = HtmlEntityCodes[entity];
		if ('number' != typeof entityCode) {
			console.error('Invalid HTML entity &' + entity + ';');
			return '';
		}
		return String.fromCharCode(entityCode);
	});
	return str;
}

var HtmlEntityCodes = {quot:34,amp:38,apos:39,lt:60,gt:62,nbsp:160,iexcl:161,cent:162,pound:163,curren:164,yen:165,brvbar:166,sect:167,uml:168,copy:169,ordf:170,laquo:171,not:172,shy:173,reg:174,macr:175,deg:176,plusmn:177,sup2:178,sup3:179,acute:180,micro:181,para:182,middot:183,cedil:184,sup1:185,ordm:186,raquo:187,frac14:188,frac12:189,frac34:190,iquest:191,Agrave:192,Aacute:193,Acirc:194,Atilde:195,Auml:196,Aring:197,AElig:198,Ccedil:199,Egrave:200,Eacute:201,Ecirc:202,Euml:203,Igrave:204,Iacute:205,Icirc:206,Iuml:207,ETH:208,Ntilde:209,Ograve:210,Oacute:211,Ocirc:212,Otilde:213,Ouml:214,times:215,Oslash:216,Ugrave:217,Uacute:218,Ucirc:219,Uuml:220,Yacute:221,THORN:222,szlig:223,agrave:224,aacute:225,acirc:226,atilde:227,auml:228,aring:229,aelig:230,ccedil:231,egrave:232,eacute:233,ecirc:234,euml:235,igrave:236,iacute:237,icirc:238,iuml:239,eth:240,ntilde:241,ograve:242,oacute:243,ocirc:244,otilde:245,ouml:246,divide:247,oslash:248,ugrave:249,uacute:250,ucirc:251,uuml:252,yacute:253,thorn:254,yuml:255,OElig:338,oelig:339,Scaron:352,scaron:353,Yuml:376,fnof:402,circ:710,tilde:732,Alpha:913,Beta:914,Gamma:915,Delta:916,Epsilon:917,Zeta:918,Eta:919,Theta:920,Iota:921,Kappa:922,Lambda:923,Mu:924,Nu:925,Xi:926,Omicron:927,Pi:928,Rho:929,Sigma:931,Tau:932,Upsilon:933,Phi:934,Chi:935,Psi:936,Omega:937,alpha:945,beta:946,gamma:947,delta:948,epsilon:949,zeta:950,eta:951,theta:952,iota:953,kappa:954,lambda:955,mu:956,nu:957,xi:958,omicron:959,pi:960,rho:961,sigmaf:962,sigma:963,tau:964,upsilon:965,phi:966,chi:967,psi:968,omega:969,thetasym:977,upsih:978,piv:982,ensp:8194,emsp:8195,thinsp:8201,zwnj:8204,zwj:8205,lrm:8206,rlm:8207,ndash:8211,mdash:8212,lsquo:8216,rsquo:8217,sbquo:8218,ldquo:8220,rdquo:8221,bdquo:8222,dagger:8224,Dagger:8225,bull:8226,hellip:8230,permil:8240,prime:8242,Prime:8243,lsaquo:8249,rsaquo:8250,oline:8254,frasl:8260,euro:8364,image:8465,weierp:8472,real:8476,trade:8482,alefsym:8501,larr:8592,uarr:8593,rarr:8594,darr:8595,harr:8596,crarr:8629,lArr:8656,uArr:8657,rArr:8658,dArr:8659,hArr:8660,forall:8704,part:8706,exist:8707,empty:8709,nabla:8711,isin:8712,notin:8713,ni:8715,prod:8719,sum:8721,minus:8722,lowast:8727,radic:8730,prop:8733,infin:8734,ang:8736,and:8743,or:8744,cap:8745,cup:8746,"int":8747,there4:8756,sim:8764,cong:8773,asymp:8776,ne:8800,equiv:8801,le:8804,ge:8805,sub:8834,sup:8835,nsub:8836,sube:8838,supe:8839,oplus:8853,otimes:8855,perp:8869,sdot:8901,lceil:8968,rceil:8969,lfloor:8970,rfloor:8971,lang:9001,rang:9002,loz:9674,spades:9824,clubs:9827,hearts:9829,diams:9830};
var KeyCodes = {STRG:17,CTRL:17,CTRLRIGHT:18,CTRLR:18,SHIFT:16,RETURN:13,ENTER:13,BACKSPACE:8,BCKSP:8,ALT:18,ALTR:17,ALTRIGHT:17,SPACE:32,WIN:91,MAC:91,FN:null,UP:38,DOWN:40,LEFT:37,RIGHT:39,ESC:27,DEL:46,F1:112,F2:113,F3:114,F4:115,F5:116,F6:117,F7:118,F8:119,F9:120,F10:121,F11:122,F12:123,backspace:8,tab:9,enter:13,shift:16,ctrl:17,alt:18,pause_break:19,caps_lock:20,escape:27,page_up:33,page_down:34,end:35,home:36,left_arrow:37,up_arrow:38,right_arrow:39,down_arrow:40,insert:45,"delete":46,0:48,1:49,2:50,3:51,4:52,5:53,6:54,7:55,8:56,9:57,a:65,b:66,c:67,d:68,e:69,f:70,g:71,h:72,i:73,j:74,k:75,l:76,m:77,n:78,o:79,p:80,q:81,r:82,s:83,t:84,u:85,v:86,w:87,x:88,y:89,z:90,left_window:91,right_window:92,select_key:93,numpad_0:96,numpad_1:97,numpad_2:98,numpad_3:99,numpad_4:100,numpad_5:101,numpad_6:102,numpad_7:103,numpad_8:104,numpad_9:105,multiply:106,add:107,subtract:109,decimal_point:110,divide:111,f1:112,f2:113,f3:114,f4:115,f5:116,f6:117,f7:118,f8:119,f9:120,f10:121,f11:122,f12:123,num_lock:144,scroll_lock:145,semi_colon:186,equal_sign:187,comma:188,dash:189,period:190,forward_slash:191,grave_accent:192,open_bracket:219,backslash:220,closebracket:221,single_quote:222}
if(Object.freeze) {
    Object.freeze(HtmlEntityCodes);
    Object.freeze(KeyCodes);
}
