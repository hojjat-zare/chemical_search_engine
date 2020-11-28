color = d3.scaleLinear()
    .domain([0, 5])
    .range(["hsl(152,80%,80%)", "hsl(228,30%,40%)"])
    .interpolate(d3.interpolateHcl);

format = d3.format(",d")

width = 600;
height = width;

pack = data => d3.pack()
    .size([width, height])
    .padding(3)
  (d3.hierarchy(data)
    .sum(d => d.value)
    .sort((a, b) => b.value - a.value));

property_type_map = {"blob":"images","entity":"conceptual","numeric":"numeric","string":"texts"};

function encapsulate_results(all_results){
  var encapsulated_results = [];
  all_results.forEach(function(result,index){
    let result_name = result.entity_name.replaceAll("_","");
    let encapsuled_result = {name:result_name}
    let result_children = [];
    Object.keys(result.data).forEach(function(key){
      property_group = {name:property_type_map[key]};
      let property_group_children = [];
      Object.keys(result.data[key]).forEach(function (key2){
        // console.log(key2)
        property = {name:key2};
        if(key == 'entity'){
          var proper_value = ( (result.data[key][key2].value.data===null) ? null : encapsulate_results(result.data[key][key2].value) );
          property.children = proper_value;
          // console.log(proper_value[0]);
        }else{
          property.children = [{name:"" + result.data[key][key2].value + " " + ((result.data[key][key2].unit===null) ? "" : result.data[key][key2].unit),value:100}];
        }
        property_group_children.push(property);
      });
      property_group.children = property_group_children;
      result_children.push(property_group);

    });
    encapsuled_result.children = result_children;
    encapsulated_results.push(encapsuled_result);
    // first = {name:result_name,children:[]};
    // console.log(encapsulated_results);
  });
  return encapsulated_results;
}
"use strict";
function modify_result(single_result){
  let level1 = {name:single_result.entity_name};
  let level1_children = [];
  Object.keys(single_result.data).forEach(function(property_group){
    let level2 = {name:property_group};
    let level2_children = [];
    Object.keys(single_result.data[property_group]).forEach(function(property_name){
      let level3 = {name:property_name};
      let level3_children = [];
      let level4 = undefined;
      let level4_children = [];
      if(property_group == 'entity'){
        if(single_result.data[property_group][property_name].value === null){
          level4 = {name:null,value:100};
        }else{
          let all_entities = single_result.data[property_group][property_name].value;
          all_entities.forEach(function(new_result,index){
            let new_modified_result = modify_result(new_result);
            level4_children.push(new_modified_result);
            // console.log(new_modified_result);
          });
          level4 = {name:"properties"};
          level4.children = level4_children;
        }
      }else{
        let dname = "" + single_result.data[property_group][property_name].value + " " + single_result.data[property_group][property_name].unit;
        level4 = {name:dname,value:100};
      }
      level3_children.push(level4);
      level3.children = level3_children;
      level2_children.push(level3);
      // console.log(level3);
    });
    level2.children = level2_children;
    level1_children.push(level2);
    // console.log(level2);
  });
  level1.children = level1_children;
  return level1;
}

// console.log(data);

// data = encapsulate_results(results)[0];
data = modify_result(results[0]);
console.log(data);
// console.log(data);

function draw() {
  const root = pack(data);
  let focus = root;
  let view;

  const svg = d3.select("svg")
      .attr("viewBox", `-${width / 2} -${height / 2} ${width} ${height}`)
      .style("display", "block")
      .style("margin", "0 -14px")
      .style("background", color(0))
      .style("cursor", "pointer")
      .on("click", (event) => zoom(event, root));

  const node = svg.append("g")
    .selectAll("circle")
    .data(root.descendants().slice(1))
    .join("circle")
      .attr("fill", d => d.children ? color(d.depth) : "white")
      .attr("pointer-events", d => !d.children ? "none" : null)
      .on("mouseover", function() { d3.select(this).attr("stroke", "#000"); })
      .on("mouseout", function() { d3.select(this).attr("stroke", null); })
      .on("click", (event, d) => focus !== d && (zoom(event, d), event.stopPropagation()));
    // console.log(root.descendants().slice(1));

  const label = svg.append("g")
      .style("font", "10px sans-serif")
      .attr("pointer-events", "none")
      .attr("text-anchor", "middle")
    .selectAll("text")
    .data(root.descendants())
    .join("text")
      .style("fill-opacity", d => d.parent === root ? 1 : 0)
      .style("display", d => d.parent === root ? "inline" : "none")
      .text(d => d.data.name);

  zoomTo([root.x, root.y, root.r * 2]);

  function zoomTo(v) {
    const k = width / v[2];

    view = v;

    label.attr("transform", d => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
    node.attr("transform", d => `translate(${(d.x - v[0]) * k},${(d.y - v[1]) * k})`);
    node.attr("r", d => d.r * k);
  }

  function zoom(event, d) {
    const focus0 = focus;

    focus = d;

    const transition = svg.transition()
        .duration(event.altKey ? 7500 : 750)
        .tween("zoom", d => {
          const i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2]);
          return t => zoomTo(i(t));
        });

    label
      .filter(function(d) { return d.parent === focus || this.style.display === "inline"; })
      .transition(transition)
        .style("fill-opacity", d => d.parent === focus ? 1 : 0)
        .on("start", function(d) { if (d.parent === focus) this.style.display = "inline"; })
        .on("end", function(d) { if (d.parent !== focus) this.style.display = "none"; });
  }
}
draw();
