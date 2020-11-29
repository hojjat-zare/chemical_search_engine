width = 1000;
tree = data => {
  const root = d3.hierarchy(data);
  root.dx = 10;
  root.dy = width / (root.height + 1);
  return d3.tree().nodeSize([root.dx, root.dy])(root);
}


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

function draw() {
  const root = tree(data);

  let x0 = Infinity;
  let x1 = -x0;
  root.each(d => {
    if (d.x > x1) x1 = d.x;
    if (d.x < x0) x0 = d.x;
  });

  const svg = d3.select("svg")
      .attr("viewBox", [0, 0, width, x1 - x0 + root.dx * 2]);

  const g = svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
      .attr("transform", `translate(${root.dy / 3},${root.dx - x0})`);

  const link = g.append("g")
    .attr("fill", "none")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.4)
    .attr("stroke-width", 1.5)
  .selectAll("path")
    .data(root.links())
    .join("path")
      .attr("d", d3.linkHorizontal()
          .x(d => d.y)
          .y(d => d.x));

  const node = g.append("g")
      .attr("stroke-linejoin", "round")
      .attr("stroke-width", 3)
    .selectAll("g")
    .data(root.descendants())
    .join("g")
      .attr("transform", d => `translate(${d.y},${d.x})`);

  node.append("circle")
      .attr("fill", d => d.children ? "#555" : "#999")
      .attr("r", 2.5);

  node.append("text")
      .attr("dy", "0.31em")
      .attr("x", d => d.children ? -6 : 6)
      .attr("text-anchor", d => d.children ? "end" : "start")
      .text(d => d.data.name)
    .clone(true).lower()
      .attr("stroke", "white");

}

draw();
