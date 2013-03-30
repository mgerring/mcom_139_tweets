var tweetavis = {
	wordcloud: {
		tweets : "",
		layout : "",
		vis : "",
		svg : "",
		collection : "",
		fill : d3.scale.category20(),
		wordScale : d3.scale.log().range([12,72]),
		barScale : d3.scale.linear().range([0,960]),
		timeScale : d3.scale.linear().range([0,100]),
		sliderEl : null,
		initslider: false,
		subject: 0,
		tweet_meta: null,
		init : function() {
			this.svg = d3.select("#chart").append("svg")
	    		.attr("width", 960)
	    		.attr("height", 500);
			this.vis = this.svg.append("g")
	    		.attr("transform", "translate(480,250)");
			this.layout = d3.layout.cloud().size([960, 500])
				.rotate(0)
				.font("Impact")
				.fontSize(function(d) { return d.size; })
				.on("end", $.proxy(this.draw, this));
		},
		getData : function(url,collection,reset) {
			this.collection = collection;
			this.tweet_meta = JSON.parse( $.ajax('/static/json/'+collection+'/'+collection+'_meta.json', {async:false} ).responseText );
			if(reset) {
				if(this.initslider) {
					this.initslider.data()['api']['options']['scale'] = [0, this.tweet_meta.length-1];
				}
				var min_time = this.tweet_meta[0];
				var max_time = this.tweet_meta[this.tweet_meta.length - 1];
				url += '/'+min_time+'-'+max_time+'.json';
			}
			$.getJSON(
				url,
				$.proxy(function(result) {
					this.tweets = result;
					var min_time = this.tweet_meta[0]
					var max_time = this.tweet_meta[this.tweet_meta.length - 1]
					this.timeScale.domain([min_time,max_time]);
					$(window).trigger('tweetdataloaded');
				}, this)
			);
		},
		generate : function() {
			var subject = this.subject;
			var count = _.map( this.tweets[subject], function(word){ return word[1] } );
			var tweets_high = _.max( count );
			var tweets_low = _.min( count );

			console.log(this.tweets);
			// display a different chart if we're looking at Romney vs Obama, because a wordcloud isn't useful.
			if( subject == 3 ) {
				this.barScale.domain([0, tweets_low+tweets_high]);
				var mapFunc = $.proxy(function(d) {
					return { text: d[0], size: this.barScale(d[1]), count: d[1] };
				},this )
				this.drawBars( this.tweets[subject].map( mapFunc ) );
			} else {
				this.wordScale.domain([tweets_low,tweets_high]);
				var mapFunc = $.proxy(function(d) {
					return { text: d[0], size: this.wordScale(d[1]) };
				},this )
				this.layout.stop()
					.words( this.tweets[subject].map( mapFunc ) )
					.start();
			}
		},
		draw : function(words) {
			console.log(words);
			if(this.subject == 3) {
				this.drawBars(words);
				return;
			}
			this.vis.selectAll("rect").remove();
			this.vis.selectAll(".label").remove();
			var text = this.vis.selectAll("text").data(words);
			text.transition()
				.text(function(d) { return d.text; })
				.duration(1000)
				.attr("transform", function(d) { return "translate(" + [d.x, d.y] + ")"; })
				.attr("text-anchor", "middle")
				.style("font-size", function(d) { return d.size + "px"; });
			text.enter().append("text")
				.style("font-size", function(d) { return d.size + "px"; })
				.style("font-family", "Impact")
				.style("fill", $.proxy(function(d, i) { return this.fill(i); }, this) )
				.attr("text-anchor", "middle")
				.attr("transform", function(d) {
					return "translate(" + [d.x, d.y] + ")";
				})
				.text(function(d) { return d.text; });
			text.exit()
				.remove();
		},
		drawBars : function(words) {
			this.vis.selectAll("text").remove();
			var labels = this.vis.selectAll("text").data(words);
			var bars = this.vis.selectAll("rect").data(words);
			  bars.transition()
			  	.duration(1000)
			  	.attr("y", function(d, i) { return i * 45; } )
			  	.attr("x", "-480")
			    .attr("width", function(d){ return d.size })
			    .attr("height", '40px');
			  bars.enter().append("rect")
			  	.attr("y", function(d, i) { return i * 45; } )
			  	.attr("x", "-480")
			    .attr("width", function(d){ return d.size })
			    .attr("height", '40px')
			    .attr("class", function(d){ return d.text });
			  labels.enter().append("text")
			  	.attr("y", function(d, i) { return (i * 45) + 22 } )
			  	.attr("x", "-480")
			  	.text(function(d){return d.text + " (" + d.count + ")"})
			  	.attr("class", "label");
			  labels
			  	.attr("y", function(d, i) { return (i * 45) + 22 } )
			  	.attr("x", "-480")
			  	.text(function(d){return d.text + " (" + d.count + ")"})
		},
		toTime: function(time) {
			return this.timeScale.invert(time);
		},
		toDate: function(time) {
			//Why are we manually lopping of the string GMT? I dunno, why are you such a bitch?
			return new Date( this.tweet_meta[time] * 1000 ).toUTCString().replace("GMT","PST");
		},
		updateTime: function(el) {
			el = $(el);
			var values = el.find("#double-slider").noUiSlider('value');
			el.find("#begin_text").text( this.toDate( values[0] ) );
			el.find("#end_text").text( this.toDate( values[1] ) );
			el.find("#begin").val( values[0] );
			el.find("#end").val( values[1] );
		},
		initSlider: function(el,form) {
			$(el).addClass('noUiSlider-container').noUiSlider('init',{	
				handles : 2, 
				connect : 'upper',
				scale	: [0, this.tweet_meta.length-1],
				start	: [0, this.tweet_meta.length-1],
				end	: $.proxy(function() {
					this.update(form,false);
					this.updateTime(form);
				},this),
				change : $.proxy(function() {
					this.updateTime(form);
				},this)
			});
			this.updateTime(form);
			return $(el);
		},
		scaleSize: function(newWidth) {
			var el = $(this.svg[0][0]).clone()
			return d3.select(el[0])
				.attr("viewBox","0 0 960 500")
				.attr("width",newWidth)
				.attr("height",newWidth*(500/960))
				.attr("preserveAspectRatio","xMinYMin")
				.attr("version",'1.1')
				.attr("xmlns","http://www.w3.org/2000/svg");
				
		},
		toUrl: function(el, reset) {
			el = $(el);
			var debate = el.find('#debate').val();
			this.subject = el.find('#subject').val();
			if( !reset ) {
				var begin = el.find('#begin').val();
				var end = el.find('#end').val();
				begin = this.tweet_meta[begin];
				end = this.tweet_meta[end];
				return {collection:debate, url:'/static/json/'+debate+'/'+begin+'-'+end+'.json'};
			}
			return {collection:debate, url:'/static/json/'+debate };
		},
		update: function(el, reset) {
			var stuff = this.toUrl(el,reset);
			this.getData( stuff['url'], stuff['collection'], reset );
		},
		getCsvLink: function(el,reset) {
			el = $(el);
			var debate = el.find('#debate').val();
			var begin = el.find('#begin').val();
			var end = el.find('#end').val();
			begin = this.tweet_meta[begin];
			end = this.tweet_meta[end];
			return '/' + debate + '/' + begin + '/' + end + '/csv';
		}
	}

}

$(window).load(function(){
	tweetavis.wordcloud.init();
	tweetavis.wordcloud.update('#controls',true);
	$(window).on('tweetdataloaded',function(e){
		$('#download').attr('href',tweetavis.wordcloud.getCsvLink('#controls',false));
		tweetavis.wordcloud.generate();
		if(tweetavis.wordcloud.initslider === false){
			tweetavis.wordcloud.initslider = tweetavis.wordcloud.initSlider('#double-slider','#controls');
		}
	});
	$('select#debate').on('change',function(){
		tweetavis.wordcloud.initslider.empty(); 
		tweetavis.wordcloud.initslider = false;
		tweetavis.wordcloud.update('#controls',true);
	});
	$('select#subject').on('change',function(){
		tweetavis.wordcloud.subject = $(this).val();
		tweetavis.wordcloud.generate();
	});
	$('#print').on('click',function(e){
		e.preventDefault();
		var el = $('<div>').html(tweetavis.wordcloud.scaleSize(3000)[0][0]);
		$(this).off('click').text('Generating image...');
		encode_to_canvas(el,'tutorial','3000');
	});
});


// FireFox's SVG renderer is broken. You can't scale an
// SVG and then render it to the canvas. You have to regenerate
// the SVG with D3 and then render it to the canvas.

// Meanwhile, Chrome's canvas is broken — while you can scale
// SVGs to the size of a building in Chrome, you can't draw them
// on to a canvas, which means you can't export a raster image.

// This was true as of March 13th of 2013.

function encode_to_canvas(el,canvas,width){
	// Add some critical information
	$("svg").attr({ version: '1.1' , xmlns:"http://www.w3.org/2000/svg"});
	var svg = $(el).clone();
	var b64 = Base64.encode(svg.html());
	var img = new Image;
	var canvas = document.createElement('canvas');
	canvas.setAttribute('width',width);
	canvas.setAttribute('height',width*(500/960));
	img.src = "data:image/svg+xml;base64,\n"+b64;
	img.onload = function() {
		var ctx = canvas.getContext('2d');
		ctx.drawImage(img,0,0);
		convert_canvas_to_image(canvas, $('#print'));
	}
}

function convert_canvas_to_image(canvas, a) {
	var ctx = canvas.getContext('2d');
	try {
		a.attr('href',canvas.toDataURL("image/png")).text('Image is ready!');
	} catch(e) {
		alert('Woops! As of March 30, 2013, downloading images from charts only works in Firefox.');
		a.remove();
	}
}

/**
*
*  Base64 encode / decode
*  http://www.webtoolkit.info/
*
**/
 
var Base64 = {
 
	// private property
	_keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
 
	// public method for encoding
	encode : function (input) {
		var output = "";
		var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = Base64._utf8_encode(input);
 
		while (i < input.length) {
 
			chr1 = input.charCodeAt(i++);
			chr2 = input.charCodeAt(i++);
			chr3 = input.charCodeAt(i++);
 
			enc1 = chr1 >> 2;
			enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
			enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
			enc4 = chr3 & 63;
 
			if (isNaN(chr2)) {
				enc3 = enc4 = 64;
			} else if (isNaN(chr3)) {
				enc4 = 64;
			}
 
			output = output +
			this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
			this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
 
		}
 
		return output;
	},
 
	// public method for decoding
	decode : function (input) {
		var output = "";
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
 
		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
 
		while (i < input.length) {
 
			enc1 = this._keyStr.indexOf(input.charAt(i++));
			enc2 = this._keyStr.indexOf(input.charAt(i++));
			enc3 = this._keyStr.indexOf(input.charAt(i++));
			enc4 = this._keyStr.indexOf(input.charAt(i++));
 
			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;
 
			output = output + String.fromCharCode(chr1);
 
			if (enc3 != 64) {
				output = output + String.fromCharCode(chr2);
			}
			if (enc4 != 64) {
				output = output + String.fromCharCode(chr3);
			}
 
		}
 
		output = Base64._utf8_decode(output);
 
		return output;
 
	},
 
	// private method for UTF-8 encoding
	_utf8_encode : function (string) {
		string = string.replace(/\r\n/g,"\n");
		var utftext = "";
 
		for (var n = 0; n < string.length; n++) {
 
			var c = string.charCodeAt(n);
 
			if (c < 128) {
				utftext += String.fromCharCode(c);
			}
			else if((c > 127) && (c < 2048)) {
				utftext += String.fromCharCode((c >> 6) | 192);
				utftext += String.fromCharCode((c & 63) | 128);
			}
			else {
				utftext += String.fromCharCode((c >> 12) | 224);
				utftext += String.fromCharCode(((c >> 6) & 63) | 128);
				utftext += String.fromCharCode((c & 63) | 128);
			}
 
		}
 
		return utftext;
	},
 
	// private method for UTF-8 decoding
	_utf8_decode : function (utftext) {
		var string = "";
		var i = 0;
		var c = c1 = c2 = 0;
 
		while ( i < utftext.length ) {
 
			c = utftext.charCodeAt(i);
 
			if (c < 128) {
				string += String.fromCharCode(c);
				i++;
			}
			else if((c > 191) && (c < 224)) {
				c2 = utftext.charCodeAt(i+1);
				string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
				i += 2;
			}
			else {
				c2 = utftext.charCodeAt(i+1);
				c3 = utftext.charCodeAt(i+2);
				string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
				i += 3;
			}
 
		}
 
		return string;
	}
 
}