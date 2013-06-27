(function () {

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


//----------------------------------------------------------------------------

}).call(this);
