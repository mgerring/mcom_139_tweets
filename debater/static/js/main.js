var tweetavis = {
	wordcloud: {
		tweets : "",
		fill : d3.scale.category20(),
		wordScale : d3.scale.log(),
		timeScale : d3.scale.linear().range([0,100]),
		layout : "",
		vis : "",
		svg : "",
		collection : "",
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
				.on("end", $.proxy(this.draw, this));this.slider('#time_range', '#controls', this.tweets.min_time, this.tweets.max_time);
		},
		getData : function(collection,begin,end) {
			this.collection = collection;
			$.getJSON(
				'/data/words/'+collection+'/'+begin+'/'+end,
				$.proxy(function(result) {
					this.tweets = result;
					this.timeScale.domain([this.tweets.min_time, this.tweets.max_time]);
					minmax = {min:this.tweets.min_time,max:this.tweets.max_time};
					$("#time_range").find("#begin").attr(minmax);
					$("#time_range").find("#end").attr(minmax);
					this.generate();
				}, this)
			);
		},
		generate : function() {
			this.wordScale.domain([this.tweets.low,this.tweets.high]).range([12,72]);
			this.layout.stop()
				.words(this.tweets.words[0].map($.proxy(function(d) {
					return { text: d[0], size: this.wordScale(d[1]) };
				},this )))
				.start();
		},
		draw : function(words) {
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
		slider: function(el,form,start_time,stop_time,step) {
			var that = this;
			$(el).data('collection',this.collection).addClass('noUiSlider-container').noUiSlider('init',{	
				handles : 2, 
				connect : 'upper',
				scale	: [0,100],
				start	: [0,100],
				end	: function() {
					values = this.noUiSlider('value');
					console.log(values);
					$(el).find("#begin").val( that.timeScale.invert(values[0]) );
					console.log( that.timeScale.invert(values[0]) );
					$(el).find("#end").val( that.timeScale.invert(values[1]) );
					console.log( that.timeScale.invert(values[1]) );
					that.update(form,false);
				}
			});
		},
		update: function(el, reset) {
			//el should be a form
			el = $(el);
			var debate = el.find('#debate').val();
			if(reset) {
				var begin = 0;
				var end = 0;
			} else {
				var begin = el.find('#begin').val();
				var end = el.find('#end').val();
			}
			this.getData(debate,begin,end);
		},
	}

}

$(window).load(function(){
	tweetavis.wordcloud.init();
	tweetavis.wordcloud.update('#controls');
	$('select#debate').on('change',function(){
		tweetavis.wordcloud.update('#controls',true);
	});
});


var twutil = {
	xscale: d3.time.scale(),
	yscale: d3.scale.linear(),
	xaxis: d3.svg.axis(),
	yaxis: d3.svg.axis(),
	setXScale: function() {
		var dates = [this.getMinDate(tweets), this.getMaxDate(tweets)];
		this.xscale.domain(dates);
		this.xscale.range([0,960]);
		return this;
	},
	setXAxis: function() {
		this.xaxis.scale(this.xscale);
		this.xaxis.ticks(d3.time.minutes, 30);
		return this;
	},
	setYScale: function() {
		var bounds = [this.getMaxCharCount(tweets), this.getMinCharCount(tweets)];
		this.yscale.domain(bounds);
		this.yscale.range([0,500]);
		return this;
	},
	setYAxis: function() {
		this.yaxis.scale(this.yscale);
		this.yaxis.orient("left");
		return this;
	},
	getMinDate: function(list) {
		var tweet = _.min(list, function(item){ return item.created_at.$date });
		return new Date(tweet.created_at.$date);
	},
	getMaxDate: function(list) {
		var tweet = _.max(list, function(item){ return item.created_at.$date });
		return new Date(tweet.created_at.$date);
	},
	getMinCharCount: function(list) {
		var tweet = _.min(list, function(item){ return item.text.length });
		return tweet.text.length;
	},
	getMaxCharCount: function(list) {
		var tweet = _.max(list, function(item){ return item.text.length });
		return tweet.text.length;
	},
	createXAxis: function(el) {
		d3.select(el).append("svg")
    		.attr("id", "xaxis")
    		.attr("class", "axis")
    		.attr("width", 960)
    		.attr("height", 30)
  			.append("g")
    		.call(this.xaxis);
    	return this;
	},
	createYAxis: function(el) {
		d3.select(el).append("svg")
    		.attr("id", "yaxis")
    		.attr("class", "axis")
    		.attr("width", 50)
    		.attr("height", 500)
			.append("g")
    		.call(this.yaxis)
    		.attr("transform", "translate(40,0)");
    	return this;
	},
	plotCharCount: function(el) {
		d3.select(el).selectAll("div")
			.data(tweets)
			.enter()
			.append("div")
				.style("background", "red")
				.style("position","absolute")
				.style("left", function(d){ return twutil.xscale( new Date(d.created_at.$date) )+"px" } )
				.style("top", function(d){ return twutil.yscale( d.text.length )+"px" } )
				.attr("class","tweet")
				.html( function(d){ return '<p class="popup">'+d.text+'</p>' } );
	}
}