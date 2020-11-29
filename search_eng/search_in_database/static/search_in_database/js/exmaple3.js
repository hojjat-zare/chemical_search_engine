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

function modify_none_entity_property(property_name,property_value){
  let mod_prop = {name:property_name.replaceAll('_', '')};
  mod_prop.children = [{name:property_value.value.toString() + ' ' + property_value.unit,value:100}]; // name = [1,2,5,7]
  return mod_prop;
}

function modify_entity_property(property_name,property_value){
  let mod_prop = {name:property_name.replaceAll('_', '')};
  mod_prop.children = [];
  property_value.value.forEach(function(value,index){ // value = {'data': {'blob': {},..................
    if(value != null){
      mod_prop.children.push(modify_result(value));
    }else{
      mod_prop.children.push({name:'none',value:100})
    }
  });
  return mod_prop;
}

"use strict";
function modify_result(single_result){
  let level1 = {name:single_result.entity_name.replaceAll('_', '')};
  level1.children = [];
  if(single_result.data != null){
    Object.keys(single_result.data).forEach(function(property_group){
      let level2 = {name:property_type_map[property_group]};
      level2.children = [];
      Object.keys(single_result.data[property_group]).forEach(function(property_name){
        // console.log(property_name);
        // console.log(single_result.data[property_group][property_name]);
        let level3 = {name:''}
        if(property_group == 'entity'){
          level3 = modify_entity_property(property_name,single_result.data[property_group][property_name]);
        }else{
          level3 = modify_none_entity_property(property_name,single_result.data[property_group][property_name]);
        }
        level2.children.push(level3);
      });
      level1.children.push(level2);
    });
  }
  return level1;
}

data = modify_result(results[0]);
console.log(data);

color = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1))

partition = data => {
  const root = d3.hierarchy(data)
      .sum(d => d.value)
      .sort((a, b) => b.height - a.height || b.value - a.value);
  return d3.partition()
      .size([height, (root.height + 1) * width / 3])
    (root);
}

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
