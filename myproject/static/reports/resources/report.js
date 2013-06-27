(function () {


//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------

var girls = [],
    boys  = [],
    anon  = [],
    ages  = [0, 0, 0, 0, 0], // 13yr, 18yr, 25yr, 35yr, 45yr, 55+, 65+
    data,
    sexratio;


// Build your arrays of data.
fbook.forEach(function (x) {
    for (var item in x) {
        if (x[item]) {
            // floor the value and convert strings to integers
            //x[item] = parseInt(x[item], 10);
            x[item] = x[item] * 100;
            // split data into different arrays by sex
            if (item.substring(0, 1) === "F") { girls.push(x[item]); }
            if (item.substring(0, 1) === "M") { boys.push(x[item]);  }
            if (item.substring(0, 1) === "U") { anon.push(x[item]);  } 
            
            // create an array ordered by age from 18 - 55
            // each index will contain the sum of that ages values
            switch (item.substring(2, 4)) {
                case "13": ages[0] += x[item]; break;
                case "18": ages[0] += x[item]; break;
                case "25": ages[1] += x[item]; break;
                case "35": ages[2] += x[item]; break;
                case "45": ages[3] += x[item]; break;
                case "55": ages[4] += x[item]; break;
                case "65": ages[0] += x[item]; break;
                default: break;  
            }
            
        }
        // set empty/missing values to zero
        else { x[item] = 0; }
    }
});


// redistribute the unknown percentage evenly across the
// two sexes so that the sum of all parts adds up to 100%. 
// Later this should change, and you should just incoperate 
// a third arc to the donut for the unknown field.
var dunno  = 10000 - (d3.sum(girls) + d3.sum(boys)),
    alloc  = dunno / (girls.length + boys.length),
    sexmap = function(x) { return (x + alloc) / 100},
    dunno_age = 10000 - d3.sum(ages);

// AGE
if (dunno_age > 0) {
    ages  = ages.map(function(x) {
        return (x + (dunno_age / ages.length)) / 100;
    });
}

// SEX
if (dunno > 0) {
    girls = girls.map(sexmap);
    boys  = boys.map(sexmap);
}
else {
    girls = girls.map(function(x) { return x / 100 });
    boys  = boys.map(function(x)  { return x / 100 });   
}


girls    = girls.reverse();
boys     = boys.reverse();
data     = girls.concat(boys);
sexratio = [d3.sum(girls), d3.sum(boys)];


//----------------------------------------------------------------------------
//----------------------------------------------------------------------------
var age_labels   = ["55+", "45 - 54", "35 - 44", "25 - 34", "18 - 24"],
    w            = 600,
    h            = 420,
    margin       = 60,
    panel_width  = (w / 2) - margin,
    panel_height = h - margin,
    bar_count    = age_labels.length,
    bar_height   = panel_height / bar_count,
    maxnum = d3.max(data),
    minnum = d3.min(data),
    bin = d3.range(0, 7),
    x   = d3.scale.linear().domain([0, maxnum]).range([0, panel_width]),
    x2  = d3.scale.linear().domain([minnum, maxnum]).range([0, panel_width]),
    y   = d3.scale.ordinal().domain(girls).rangeBands([0, panel_height]),
    y2  = d3.scale.ordinal().domain(boys).rangeBands([0, panel_height]),
    y3  = d3.scale.linear().domain([0, bar_count]).range([bar_height/2, panel_height]),
    z   = d3.scale.linear().domain([0, 6]).range([0, panel_width]);
    

var chart = d3.select("#barchart").append("svg:svg")
    .attr("id", "demographic_chart")
    .attr("width", w)
    .attr("height", h)
  .append("svg:g")
    .attr("transform", "translate(0, 30)");

//----------------------------------------------------------------------------
//  LEFT SIDE
//----------------------------------------------------------------------------  
var leftside = chart.append("svg:g")
    .attr("height", panel_height)
    .attr("width", panel_width);

// vertical lines
leftside.selectAll("line")
    .data(bin)
    .enter().append("svg:line")
    .attr("x1", function(d, i) { return z(i) + 0.5; })
    .attr("y1", 0)
    .attr("x2", function(d, i) { return z(i) + 0.5; })
    .attr("y2", panel_height)
    .attr("stroke", "#555")
    .attr("stroke-width", 1);

// bars
leftside.selectAll("rect.male_rect")
    .data(boys, function(d) { return d.id; })
    .enter().append("svg:rect")
    .attr("class", "male_rect")
    .attr("x", function(d) {
        if (d == minnum && minnum != 0) { return panel_width - 5; }
        return panel_width - x2(d); 
    })
    .attr("y", function(d, i)   { return y3(i); })
    .attr("width", function(d)  { 
        if (d == minnum && minnum != 0) { return 5; }
        return x2(d); 
    })
    .attr("height", function(d) { return bar_height/4; });

//----------------------------------------------------------------------------
//  RIGHT SIDE
//----------------------------------------------------------------------------
var rightside = chart.append("svg:g")
    .attr("height", panel_height)
    .attr("width", panel_width)
    .attr("transform", "translate(" + (panel_width + margin * 2) + ", 0)");

// vertical lines
rightside.selectAll("line").data(bin).enter().append("svg:line")
    .attr("x1", function(d, i) { return z(i) - 0.5; })
    .attr("y1", 0)
    .attr("x2", function(d, i) { return z(i) - 0.5;})
    .attr("y2", panel_height)
    .attr("stroke", "#555");

// bars
rightside.selectAll("rect.female_rect")
    .data(girls, function(d) { return d.id; })
    .enter().append("svg:rect")
    .attr("class", "female_rect")
    .attr("x", 0)
    .attr("y", function(d, i)   { return y3(i); })
    .attr("width", function(d)  { return x2(d); })
    .attr("height", function(d) { return bar_height/4; });


//-------------------------------------------------------------------------
// Center Labels
//-------------------------------------------------------------------------

var labels = chart.append("svg:g")
    .attr("height", panel_height)
    .attr("width", margin * 2)
    .attr("transform", "translate(240, 0)")
    .selectAll("text.yAxisLabels");


labels.data(age_labels).enter().append("svg:text")
    .attr("class", "demographic_text")
    .attr("width", 120)
    .attr("x", 60)
    .attr("y", function(d, i) { return y3(i) + bar_height/bar_count; })
    .attr("text-anchor", "middle")
    .text(String);

//-------------------------------------------------------------------------
// AGE
//-------------------------------------------------------------------------
d3.select("#demographic_chart").append("svg:text")
    .attr("x", w / 2)
    .attr("y", 30)
    .attr("font-size", "14px")
    .attr("fill", "#FFF")
    .attr("text-anchor", "middle")
    .attr("class", "age_label")
    .text("AGE");

d3.select("#demographic_chart").append("svg:line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", w)
    .attr("y2", 0)
    .attr("stroke", "#9f9f9f");
    

//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
// PIE CHART


var w  = 300,                // width
    h  = 300,                // height
    r1 = Math.min(w, h) / 2, // radius big   (150px)
    r0 = r1 * .6,            // radius small (90px)
    speed = 200,             // speed of transition
    arc   = d3.svg.arc(),
    donut = d3.layout.pie(),
    data0 = sexratio.sort().reverse(),
    data1 = ages,
    demo_title,
    demo_color,
    // age_labels = ["65+", "55+", "45 - 54", "35 - 44", "25 - 34", "18 - 24", "13-17"],
    sex_colors = ['#FFB2C0', '#336CA4'],
    age_colors = ["#679ED2", "#408AD2", "#336CA4", "#0C5AA6", "#04396C"];
    

var demopie = [
    {"title":"SEX", "data":data0, "color":sex_colors, "labels":['female', 'male']},
    {"title":"AGE", "data":data1, "color":age_colors, "labels":age_labels.reverse()}
];

//console.log(ages);

//-------------------------------------------------------------------------
// Initialize canvas
//-------------------------------------------------------------------------

// create your svg canvas
var vis = d3.select('#demographic_pie').append('svg:svg')
    .attr('width', w)
    .attr('height', h);

// append the default sex donut to canvas onLoad
vis.selectAll('g.arc').call(makeArcs, arcss(data0));

// set listener on radio buttons
d3.selectAll('button[name=demodonut]').on('click', changedonut);


//-------------------------------------------------------------------------
// Callback Functions
//-------------------------------------------------------------------------

function changedonut() {
    // fade all the current arcs to 0% opacity
    // and after last arc fades, create new chart
    var data = this.value === 'sex' ? data1 : data0;
    
    var archy = d3.selectAll('g.arc > path')
        .data(arcss(data))
        .transition().duration(speed)
        .delay(function(d, i) { return i * speed; })
        .attr('opacity', 0)
        .each('end', function(d, i) {
            if (i+1 === data.length) { newPie(i); }
        });
}


function arcss(data) {
    // this function returns an array
    // of properties for making arcs.
    var arcs = donut(data), arc, i = -1;
    
    while (++i < data.length) {
        arc = arcs[i];
        arc.innerRadius = r0;
        arc.outerRadius = r1;
    }
    return arcs;
}


function newPie(i) {
    // remove all existing arc elements
    // and append the new ones in its place.
    var data = i > 3 ? arcss(data0) : arcss(data1);
    d3.selectAll('g.arc').remove(); 
    vis.selectAll('g.arc').call(makeArcs, data); 
}

function makeArcs(selection, data) {
    // From the data provided, create 
    // the arcs that make up the donut
    if (data.length < 3) {
        demo_title = demopie[0].title;
        demo_color = demopie[0].color;
        demo_label = demopie[0].labels;
    }
    else {
        demo_title = demopie[1].title;
        demo_color = demopie[1].color;
        demo_label = demopie[1].labels;
    }
    
    var archs = selection.data(data)
        .enter().append('svg:g')
        .attr('class', 'arc')
        .attr("transform", "translate(" + r1 + "," + r1 + ")");
    
    archs.append("svg:path")
        .attr('opacity', 0)
        .attr('fill', function(d, i) { return demo_color[i]; })
        .attr('d', arc);

    archs.append("svg:text")
        .attr("transform", function(d) {
            return "translate(" + arc.centroid(d) + ")";
        })
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .attr("class", "donut_text")
        .text(function(d) {
            // dont return values smaller than 3, b/c there 
            // will not be enough space in arc to fit text
            if (d.value <= 3) { return ' '; }
            else { return d.value.toFixed(1) + '%'; }
        });
    
    archs.append("svg:text")
        .attr("trasform", "translate(" + w/2 + "," + h/2 + ")")
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .attr("class", "donut_text_title")
        .text(demo_title);
    
    // fade the arcs in one at a time.
    d3.selectAll('g.arc > path')
        .transition().duration(speed)
        .delay(function(d, i) { return i * speed; })
        .attr('opacity', 1);
    
    // make the legend
    makeLegend(data, demo_color, demo_label);
}



//-------------------------------------------------------------------------
// Create Legend
//-------------------------------------------------------------------------
// demo_pie_legend

function makeLegend(data, demo_color, demo_label) {
    
    var box_height    = 30,
        legend_height = h - box_height * 2,
        box_padding   = ((legend_height / data.length) - 30) / 2;
    
    // remove any prexisting boxes on transition
    d3.selectAll('.legend_box_wrapper').remove();
    
    // create new legend for the current pie chart
    var leg = d3.select('#demo_pie_legend').append('div')
        .attr('class', 'legend_wrapper');

    leg.selectAll('div').data(data)
        .enter().append('div')
        .attr('class', 'legend_box_wrapper')
        .style('padding-top', function(d, i)    { return box_padding + 'px'; })
        .style('padding-bottom', function(d, i) { return box_padding + 'px'; })
      .append('div')
        .attr('class', 'legend_box')
        .style('background-color', function(d, i) {
            return demo_color[i];
        });

    leg.selectAll('.legend_box_wrapper')
        .append('div')
        .attr('class', 'legend_box_label')
        .text(function(d, i) {
            return demo_label[i];
        });  
}


//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
// CALENDAR

// ~~ below is bitwise way of rounding down with math.floor()
// >> converts z to its binary form & shifts it 1-bit to the right
// 34 = 100010  (<<)
// 17 = 10001
//  8 = 1000    (>>)
var w  = 960,                          // width
    m  = [15, 15, 15, 30]              // margin - top right bottom left
    z  = ~~((w - (m[1] + m[3])) / 53), // year width * 2 / floor(weeks) = 17
    ph = z >> 1,                       // padding height = 8
    h  = z * 7 + m[0],                 // height = 8 * 7 + 15 = 134
    cal_months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
    m_position = d3.scale.ordinal().domain(cal_months).rangeBands([w-z, 0]);


// create a new canvas for each calendar year
var cal = d3.select('#report_calendar').selectAll('svg')
    .data(d3.range(2010, 2011))
    .enter().append('svg:svg')
    .attr('width', w)
    .attr('height', h + ph * 2)
    .attr('class', 'RdYlGn')
  .append('svg:g')
    .attr('class', 'calendar_g')
    .attr('transform', 'translate('+ m[3] +','+ (ph+m[0]) +')');

// add the year label to the calendar
cal.append('svg:text')
    .attr('transform', 'translate(-6,'+ h/2 +') rotate(-90)')
    .attr('class', 'calendar_year')
    .attr('text-anchor', 'middle')
    .text(function(d) { return d; });

// add the month labels
cal.selectAll('path.month')
    .data(calendar.months)
    .enter().append('svg:text')
    .attr('class', 'cal_month_label')
    .attr('transform', function(d, i) {
        var mnth = (d.firstWeek + 1) * z;
        return 'translate('+ (mnth + z * 2) +', -5)';
    })
    .attr('text-anchor', 'middle')
    .text(function(d, i) { return cal_months[i]; });

// create and position each day in the month
cal.selectAll('rect.day')
    .data(calendar.dates)
    .enter().append('svg:rect')
    .attr('x', function(d) { return d.week * z; })
    .attr('y', function(d) { return d.day * z;  })
    .attr('class', 'day')
    .attr('width', z)
    .attr('height', z);

// draw a path around each month
cal.selectAll("path.month")
    .data(calendar.months)
    .enter().append("svg:path")
    .attr("class", "month")
    .attr("d", function(d) {
      return "M" + (d.firstWeek + 1) * z + "," + d.firstDay * z
           + "H" + d.firstWeek * z
           + "V" + 7 * z
           + "H" + d.lastWeek * z
           + "V" + (d.lastDay + 1) * z
           + "H" + (d.lastWeek + 1) * z
           + "V" + 0
           + "H" + (d.firstWeek + 1) * z
           + "Z";
    });

// the +1's used above is to make space for the 1px border
// M - moveto
// H - horizontal line to
// V - vertical line to
// Z - closepath

d3.csv(active_csv, function(csv) {
    var data = d3.nest()
        .key(function(d) { return d.Date; }) // key is the date
        .rollup(function(d) { 
            return (d[0].Close - d[0].Open) / d[0].Open;  // % growth in stock
        })
        .map(csv);

    var color = d3.scale.quantize()
        .domain([-.05, .05])
        .range(d3.range(9));
    
    cal.selectAll("rect.day")
        .attr("class", function(d) { 
            return "day q" + color(data[d.Date]) + "-9"; 
        })
        .append("svg:title")
        .text(function(d) { 
            return d.Date + ": " + (data[d.Date] * 100).toFixed(1) + "%"; 
        });
});

//-------------------------------------------------------------------------
// Initialize canvas
//-------------------------------------------------------------------------

/*
Date        2010-10-01, 
Open        10789.72,
High        10907.41,
Low         10759.14,
Close       10829.68,
Volume      4298910000,
Adj Close   10829.68

*/


//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
// RATINGS LINE GRAPH

var m = [50, 50, 50, 50],
    w = 620 - m[1] - m[3],
    h = 400 - m[0] - m[2],
    parse   = d3.time.format("%b %Y").parse, 
    format  = d3.time.format("%b %y"),
    toggler = 1;


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
    .y1(function(d) { return y(d.rating); });

// A line generator, for the dark stroke.
var line = d3.svg.line()
    .interpolate("monotone")
    .x(function(d) { return x(d.date); })
    .y(function(d) { return y(d.rating); });


// get data from csv file TODO: replace this with data from Django DB
/*
var parse_date = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

// NOTE
// you should create a new javascript object from this
// and save it into: var values
// you can then remove the d3.csv() function below and
// you can just let the currently existing code do its work.

  
aptratings_json.forEach(function(data) {
    data.date = new XDate(data.date).toString("MMM yyyy");
    data.rating = +data.total_overall_rating;
    
});

*/

d3.csv(linegraph_csv, function(data) {
    
    // Filter to one property;
    var values = data.filter(function(d) {
        console.log(aptrating_property);
        //d.alias = aptrating_property ? aptrating_property : "";
        return d.alias == 'DOMAIN'; // aptrating_property declared in html
    });
    
    // Parse dates and numbers. We assume values are sorted by date.
    values.forEach(function(d) {
        d.date   = parse(d.date);
        d.rating = +d.rating;
    });
    
    // Compute the minimum and maximum date, and the maximum rating.
    x.domain([values[0].date, values[values.length - 1].date]);
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
        .attr("d", area(values));
    
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
        .attr("d", line(values));
    
    // Add a small label for the alias name.
    svg.append("svg:text")
        .attr("x", w - 6)
        .attr("y", h - 6)
        .attr("text-anchor", "end")
        .text(aptrating_property.toUpperCase() + " RATINGS");
        //.text(values[0].alias + " RATINGS");
    
    // On click, update the x-axis.
    svg.on("click", function() {
        
        var mouse_local = mouselocation(),
            n = values.length - 1, // total number of months in data
            i = Math.floor(mouse_local / (w / n)),
            j = i + 1;
        
        toggler += 1; // tracks year vs month view
        
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
        
        x.domain([values[i].date, values[j].date]);
        var t = svg.transition().duration(750);
        t.select(".x.axis").call(xAxis);
        t.select(".area").attr("d", area(values));
        t.select(".line").attr("d", line(values));
    });
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


//----------------------------------------------------------------------------
/* TODO
    
    - NOTE MISSNG Age range for 13-17
    
    - if a specific age = 0, then it breaks the pie chart
      fix it so that 0 creates an invisible bar
      
    - extract relevant insights data into CSV file
    - get number of years that data has been kept
    - create as many calendars as there have been years that data was kept
    - after 10 days of a new month have gone by hotness/coldness of that 
      months day-colors will be chosen relative to the domain of all days 
      in that given month.
    - prior to the 10 day mark (e.g. if your on day 9) days will be colored
      relative to the domain of all previous months days + the days that
      have gone by in the current month.
      
    - insert % into boys and girls bars on pyramid graph
    - style the radio buttons on pie chart
    - generate map-keys for all of your graphs
    - associate proper color to proper sex. To do this you will need to sort()
      and reverse() the data before you declare your initial variables.
    
    - build the calendar
    - build the custom graph for activity

*/
}).call(this);
