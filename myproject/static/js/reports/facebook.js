(function () {


//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
// FACEBOOK SEX-AGE DEMOGRAPHIC VERTICAL BAR CHART

var girls = [],
    boys  = [],
    anon  = [],
    ages  = [0, 0, 0, 0, 0, 0], // 13yr, 18yr, 25yr, 35yr, 45yr, 55+, 65+
    data,
    girl_percentage,
    boy_percentage,
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


girls = girls.reverse();
boys  = boys.reverse();
data  = girls.concat(boys);

girl_percentage = Math.round(100*(d3.sum(girls) / d3.sum(data)));
boy_percentage  = 100 - girl_percentage;
sexratio        = [girl_percentage, boy_percentage];

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------
var age_labels   = ["55+", "45 - 54", "35 - 44", "25 - 34", "18 - 24", "13 - 17"],
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
    data1 = ages.map(function(x) { return ((x/100)/(d3.sum(ages)/100))*100 }),
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

//----------------------------------------------------------------------------

}).call(this);
