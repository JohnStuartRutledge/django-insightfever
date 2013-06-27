(function () {

//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
// APARTMENT RATINGS LINE GRAPH

var m = [50, 50, 50, 50],
    w = 620 - m[1] - m[3],
    h = 400 - m[0] - m[2],
    parse_date = d3.time.format("%Y-%m-%dT%H:%M:%S").parse,
    format     = d3.time.format("%b %y"),
    toggler    = 1;


aptratings_json.forEach(function(d) {
    d.date = parse_date(d.created_on);
    //d.date = new XDate(d.created_on).toString("MMM yyyy");
});


// Scales and axes. Note the inverted domain for the y-scale: bigger is up!
var x = d3.time.scale(), // scale.tickFormat(count)
    y = d3.scale.linear().range([h, 0]),
    xAxis = d3.svg.axis().scale(x).tickSize(-h).tickFormat(format).tickSubdivide(true),
    yAxis = d3.svg.axis().scale(y).ticks(4).orient("right");

x.range([0, w]);

// An area generator, for the light fill.
var area = d3.svg.area()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y0(h)
    .y1(function(d) { return y(d.recommended_by); });

// A line generator, for the dark stroke.
var line = d3.svg.line()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.recommended_by); });


// Compute the minimum and maximum date, and the maximum rating.
x.domain([aptratings_json[0].date, 
    aptratings_json[aptratings_json.length - 1].date]);

y.domain([0, 100]).nice();


// Add an SVG element with the desired dimensions and margin.
var svg = d3.select("#ratings_graph").append("svg:svg")
    .attr("width",  w + m[1] + m[3])
    .attr("height", h + m[0] + m[2])
  .append("svg:g")
    .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

// Add the clip path.
svg.append("svg:clipPath")
    .attr("id", "clip")
    .append("svg:rect")
    .attr("width", w)
    .attr("height", h);

// Add the area path.
svg.append("svg:path")
    .attr("class", "area")
    .attr("clip-path", "url(#clip)")
    .attr("d", area(aptratings_json));

// Add the x-axis.
svg.append("svg:g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + h + ")")
    .call(xAxis);

// Add the y-axis.
svg.append("svg:g")
    .attr("class", "y axis")
    .attr("transform", "translate(" + w + ",0)")
    .call(yAxis);

// Add the line path.
svg.append("svg:path")
    .attr("class", "line")
    .attr("clip-path", "url(#clip)")
    .attr("d", line(aptratings_json));

// Add a small label for the alias name.
svg.append("svg:text")
    .attr("x", w - 6)
    .attr("y", h - 6)
    .attr("text-anchor", "end")
    .text(aptrating_property.toUpperCase() + " RATINGS");
    //.text(aptratings_json[0].alias + " RATINGS");

// On click, update the x-axis.
svg.on("click", function() {
    
    var mouse_local = mouselocation(),
        n = aptratings_json.length - 1, // total number of months in data
        i = Math.floor(mouse_local / (w / n)),
        j = i + 1;
    
    toggler += 1; // tracks year vs month view
    
    // TODO - fix this graph so that if months < 2 
    //        that the graph doesnt break like it currently is
    if (n == 0) {
        // render this as a single flat line
        console.log('there is only one months worth of data');
    } else if (n == 1) {
        console.log('there are only two months worth of data');
    }
    
    
    // every 2nd click return to year view
    if (toggler % 2 == 1) {
        i = 0;
        j = n;
        // format the X-axis tick labels: e.g., Jan 11
        xAxis = d3.svg.axis()
                    .scale(x)
                    .tickSize(-h)
                    .tickFormat(d3.time.format("%b %y"))
                    .tickSubdivide(true);
    } else {
        // format the X-axis tick labels: e.g., 15
        xAxis = d3.svg.axis()
                    .scale(x)
                    .tickSize(-h)
                    .tickFormat(d3.time.format("%d"))
                    .tickSubdivide(true);
        
        // TODO - consider adding the month label
        //        maybe in bottom left of graph here
        //        similar to label in bottom right.
    }
    console.log([aptratings_json[i].date, aptratings_json[j].date]);
    
    x.domain([aptratings_json[i].date, aptratings_json[j].date]);
    var t = svg.transition().duration(750);
    t.select(".x.axis").call(xAxis);
    t.select(".area").attr("d", area(aptratings_json));
    t.select(".line").attr("d", line(aptratings_json));
});


function getOffset( el ) {
    // this function returns a number to help offset
    // the mouses x-coordinate so the 0 point becomes
    // the upper left hand corner of the svg element.
    var _x = 0;
    var _y = 0;
    while( el && !isNaN( el.offsetLeft ) && !isNaN( el.offsetTop ) ) {
        _x += el.offsetLeft - el.scrollLeft;
        _y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return { top: _y, left: _x };
}

function mouselocation() {
    // return X-axis location of cursor w/in svg element
    var offset = getOffset( document.getElementById('ratings_graph') ).left;
    var xcoord = (d3.event.pageX - offset) - m[3];
    return xcoord;
}


//----------------------------------------------------------------------------

}).call(this);
