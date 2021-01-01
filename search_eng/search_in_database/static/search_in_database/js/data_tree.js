margin = ({top: 10, right: 120, bottom: 10, left: 40});
width = 900;
dy = width / 5;
dx = 30;
tree = d3.tree().nodeSize([dx, dy]);
diagonal = d3.linkHorizontal().x(d => d.y).y(d => d.x)


property_type_map = {"blob":"images","entity":"conceptual","numeric":"numeric","string":"texts"};

function modify_none_entity_property(property_name,property_value){
  let mod_prop = {name:property_name.replaceAll('_', '')};
  if(property_value.unit === undefined){
    mod_prop.children = [{name:property_value.value.toString()}]; // name = [1,2,5,7]
  }else{
    mod_prop.children = [{name:property_value.value.toString() + ' ' + property_value.unit}]; // name = [1,2,5,7]
  }
  return mod_prop;
}

function modify_entity_property(property_name,property_value){
  let mod_prop = {name:property_name.replaceAll('_', '')};
  mod_prop.children = [];
  property_value.value.forEach(function(value,index){ // value = {'data': {'blob': {},..................
    if(value != null){
      mod_prop.children.push(modify_result(value));
    }else{
      mod_prop.children.push({name:'none'})
    }
  });
  return mod_prop;
}

found_entities = [];
"use strict";
function modify_result(single_result){
  let level1 = {name:single_result.entity_name.replaceAll('_', '')};
  if(!(level1.name in found_entities)){
    found_entities.push(single_result.entity_name);
    level1.children = [];
    if(single_result.data != null){
      Object.keys(single_result.data).forEach(function(property_group){
        Object.keys(single_result.data[property_group]).forEach(function(property_name){
          let level3 = {name:''}
          if(property_group == 'entity'){
            level3 = modify_entity_property(property_name,single_result.data[property_group][property_name]);
          }else{
            level3 = modify_none_entity_property(property_name,single_result.data[property_group][property_name]);
          }
          level1.children.push(level3);
        });
      });
    }
  }else{
    // level1.value = 100;
  }
  return level1;
}

data = modify_result(results[0]);

function draw() {

  const svg_container = d3.select(".svg_container")
  .style("overflow","scroll");

  const root = d3.hierarchy(data);

  root.x0 = dy / 2;
  root.y0 = 0;
  root.descendants().forEach((d, i) => {
    d.id = i;
    d._children = d.children;
    if (d.depth && d.data.name.length !== 7) d.children = null;
  });

  // console.log(root.descendants());

  const svg = d3.select("svg")
      .attr("viewBox", [-margin.left, -margin.top, width, dx])
      .style("width","5100px")
      .style("font", "8px sans-serif")
      .style("user-select", "none");

  const gLink = svg.append("g")
      .attr("fill", "none")
      .attr("stroke", "#555")
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", 1.5);

  const gNode = svg.append("g")
      .attr("cursor", "pointer")
      .attr("pointer-events", "all");

  function update(source) {
    const duration = d3.event && d3.event.altKey ? 2500 : 250;
    const nodes = root.descendants().reverse();
    const links = root.links();

    // Compute the new tree layout.
    tree(root);

    let left = root;
    let right = root;
    root.eachBefore(node => {
      if (node.x < left.x) left = node;
      if (node.x > right.x) right = node;
    });

    const height = right.x - left.x + margin.top + margin.bottom;

    // svg.attr("viewBox",[-margin.left, left.x - margin.top, width, height])

    const transition = svg.transition()
        .duration(duration)
        .attr("viewBox", [-margin.left, left.x - margin.top- height/10, width*5, height*1.4])
        .tween("resize", window.ResizeObserver ? null : () => () => svg.dispatch("toggle"));

    // Update the nodes…
    const node = gNode.selectAll("g")
      .data(nodes, d => d.id);

    // Enter any new nodes at the parent's previous position.
    const nodeEnter = node.enter().append("g")
        .attr("transform", d => `translate(${source.y0},${source.x0})`)
        .attr("fill-opacity", 0)
        .attr("stroke-opacity", 0)
        .on("click", (event, d) => {
          d.children = d.children ? null : d._children;
          update(d);
        });

    nodeEnter.append("circle")
        .attr("r", 2.5)
        .attr("fill", d => d._children ? "#555" : "#999")
        .attr("stroke-width", 10);

    nodeEnter.append("text")
        .attr("dy", "0.31em")
        .attr("x", d => 6)
        .attr("text-anchor", d => "start")
        .text(d => d.data.name)
        .clone(true).lower()
        .attr("stroke-linejoin", "round")
        .attr("stroke-width", 3)
        .attr("stroke", "white");

    // Transition nodes to their new position.
    const nodeUpdate = node.merge(nodeEnter).transition(transition)
        .attr("transform", d => `translate(${d.y},${d.x})`)
        .attr("fill-opacity", 1)
        .attr("stroke-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    const nodeExit = node.exit().transition(transition).remove()
        .attr("transform", d => `translate(${source.y},${source.x})`)
        .attr("fill-opacity", 0)
        .attr("stroke-opacity", 0);

    // Update the links…
    const link = gLink.selectAll("path")
      .data(links, d => d.target.id);

    // Enter any new links at the parent's previous position.
    const linkEnter = link.enter().append("path")
        .attr("d", d => {
          const o = {x: source.x0, y: source.y0};
          return diagonal({source: o, target: o});
        });

    // Transition links to their new position.
    link.merge(linkEnter).transition(transition)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition(transition).remove()
        .attr("d", d => {
          const o = {x: source.x, y: source.y};
          return diagonal({source: o, target: o});
        });

    // Stash the old positions for transition.
    root.eachBefore(d => {
      d.x0 = d.x;
      d.y0 = d.y;
    });
  }
  update(root);
}
draw();
