
var margin = {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  },
  width = null;
height = null;

var linkedByIndex = {};
const isConnectedAsSource = (a, b) => linkedByIndex[`${a},${b}`];
const isConnectedAsTarget = (a, b) => linkedByIndex[`${b},${a}`];
const isConnected = (a, b) => isConnectedAsTarget(a, b) || isConnectedAsSource(a, b) || a === b;

var selectedNode = {
  root: undefined,
  linked: []
}

var node_color = d3.scaleOrdinal(d3.schemeCategory10);
var zoom = d3.zoom()
  .scaleExtent([1 / 4, 4])
  .on('zoom.zoom', function () {
    const {
      transform
    } = d3.event;
    network_group.attr("transform", transform);
  });
var svg;
var network_group;
var force_simulation = null;


function initialize() {
  margin = {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  },
    width = js_chart.offsetWidth;
  height = js_chart.offsetHeight;

  svg = d3.select("#js_chart")
    .append("svg")
    .attr("width", width - margin.left - margin.right)
    .attr("height", height - margin.top - margin.bottom)
    .call(zoom)
    .on("click", d => mouseClickFunction(d));

  network_group = svg.append("g")
    .attr("class", ".network_group");

}

function removeNetwork() {
  svg.remove()
  document.querySelector('#general-information-methods').innerHTML = "";
  console.log('Previous Network-View deleted.')
}

function sidebarCollapseJS() {
  $('.sidebar').toggleClass('active');
  $('#sidebarCollapse').toggleClass('active');
}

function drawNetwork(graph) {
  console.log(graph)

  fillSidebarGeneralInformation(graph.information)

  // fill linkedByIndex object with with sources and targets
  graph.links.forEach(d => {
    linkedByIndex[`${d.source},${d.target}`] = true;
  });

  // Add arrows for each link
  svg.append('defs')
    .selectAll("marker")
    .data(graph.links)
    .enter()
    .append("marker")
    .attr('id', d => `end-arrowhead-${d.edges[0].source}-${d.edges[0].target}`)
    .attr('viewBox', '-0 -5 10 10')
    .attr('refX', 25)
    .attr('refY', 0)
    .attr('orient', 'auto')
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('xoverflow', 'visible')
    .append('svg:path')
    .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
    .attr('fill', d => d.edge_color)
    .style('stroke', 'none');

  svg.append('defs')
    .selectAll("marker")
    .data(graph.links)
    .enter()
    .append("marker")
    .attr('id', d => `start-arrowhead-${d.edges[0].source}-${d.edges[0].target}`)
    .attr('viewBox', '-0 -5 10 10')
    .attr('refX', 25)
    .attr('refY', 0)
    .attr('orient', 'auto-start-reverse')
    .attr('markerWidth', 3)
    .attr('markerHeight', 3)
    .attr('xoverflow', 'visible')
    .append('svg:path')
    .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
    .attr('fill', d => d.edge_color)
    .style('stroke', 'none');

  // Add links to force graph
  var link = network_group
    .selectAll("line")
    .data(graph.links)
    .enter()
    .append("line")
    .attr("class", "link")
    .style("stroke", function (d) {
      return d.edge_color;
    })
    .attr("stroke-width", 3)
    .attr('marker-end', d => `url(#end-arrowhead-${d.edges[0].source}-${d.edges[0].target})`)
    .attr('marker-start', function (d) {
      if (d.edges.length > 1) {
        return `url(#start-arrowhead-${d.edges[0].source}-${d.edges[0].target})`;
      }
    });

  // Add nodes to force graph
  var node = network_group
    .selectAll("g")
    .data(graph.nodes)
    .enter()
    .append("g")
    .attr("class", "node")
    .on('click', d => mouseClickFunction(d));

  // Draw a circle for every node
  node.append("circle")
    .attr("r", "15px")
    .style("fill", d => node_color(d.id));

  // Append an Id-text for every circle
  node.append("text")
    .attr('text-anchor', 'middle')
    .attr('y', '1')
    .style('font-size', '10px')
    .attr('fill', 'white')
    .text(d => d.id);

  // Add forces between nodes and place links
  useForce(graph.nodes, graph.links, node, link);

  // Add resize event
  window.onresize = () => zoomFit(500);
}


function getPredictionScore(link){
  return link.edges.reduce(function (a, b) {
    return a + b['prediction_score'];
  }, 0);
}


function useForce(nodes, links, node, link) {

  var weightScale = d3.scaleLinear()
    .domain(d3.extent(links, d => getPredictionScore(d)))
    .range([0.05, 0.2])

  force_simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink()
      .id(function (d) {
        return d.id;
      })
      // https://github.com/d3/d3-force#link_strength
      .strength(function(d){
        return weightScale(getPredictionScore(d));
      })
      .links(links)
    )
    .force("charge", d3.forceManyBody().strength(-4000))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .on("tick", function () {
      self.ticked(node, link);
    })
    .on("end", function () {
      zoomFit(500);
    });
}


function ticked(node, link) {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);
  node.attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
}


function zoomStep(step) {
  width = js_chart.offsetWidth - 70;
  height = js_chart.offsetHeight;
  node_zoom = d3.zoomTransform(svg.node());
  zoom.scaleBy(svg.transition().duration(200), step);
}


function zoomFit(transitionDuration) {
  width = js_chart.offsetWidth;
  height = js_chart.offsetHeight;
  svg.attr("width", width).attr("height", height);

  var bounds = network_group.node().getBBox();

  var fullWidth = width - 70,
    fullHeight = height;

  var width = bounds.width,
    height = bounds.height;
  var midX = bounds.x + width / 2,
    midY = bounds.y + height / 2;
  if (width == 0 || height == 0) return; // nothing to fit
  var scale = 0.85 / Math.max(width / fullWidth, height / fullHeight);
  var translate = [fullWidth / 2 - scale * midX + 70, fullHeight / 2 - scale * midY];

  var transform = d3.zoomIdentity
    .translate(translate[0], translate[1])
    .scale(scale);

  svg
    .transition()
    .duration(transitionDuration || 0) // milliseconds
    .call(zoom.transform, transform);
}


function mouseClickFunction(d) {
  // we don't want the click event bubble up to svg
  d3.event.stopPropagation();
  nodes = d3.selectAll(".node circle");
  links = d3.selectAll(".link");
  arrows = d3.selectAll("defs marker path")

  considerSingleLink = false;
  connectedLink = [];

  if (!d3.event.ctrlKey && !d3.event.metaKey) {
    if (d === undefined) {
      selectedNode['root'] = undefined;
    } else if (d !== selectedNode['root']) {
      selectedNode['root'] = d;
    }
    selectedNode['linked'] = [];
  } else {
    if (selectedNode['root'] !== undefined &&
      selectedNode['root'] !== d &&
      selectedNode['linked'].includes(d)) {
      considerSingleLink = true;
    } else {
      return;
    }
  }

  nodes.each(function () {
    element = d3.select(this);
    if (element.data().length === 0) {
      return;
    }
    o = element.data()[0];
    if (d === undefined ||
      considerSingleLink && (o === selectedNode['root'] || o === d)) {
      styleFill(element, node_color(o.id), 1, 500);
    } else if (!considerSingleLink && isConnected(o.id, d.id)) {
      selectedNode['linked'].push(o);
      styleFill(element, node_color(o.id), 1, 500);
    } else {
      styleFill(element, d3.rgb(220, 220, 220), 0.1, 500);
    }
  });

  links.each(function (i) {
    element = d3.select(this);
    if (element.data().length === 0) {
      return;
    }
    o = element.data()[0];
    if (d === undefined ||
      !considerSingleLink && (o.source === d || o.target === d)) {
      styleStroke(element, o.edge_color, 1, 500);
    } else if (considerSingleLink &&
      (o.source === selectedNode['root'] && o.target === d ||
        o.source === d && o.target === selectedNode['root'])) {
      connectedLink = {
        rawElement: links.nodes()[i],
        elementData: o
      };
      styleStroke(element, o.edge_color, 1, 500);
    } else {
      styleStroke(element, d3.rgb(220, 220, 220), 0.1, 500);
    }
  })

  arrows
    .transition(500)
    .attr('fill', o => {
      if (d === undefined ||
        !considerSingleLink && (o.source === d || o.target === d)) {
        return o.edge_color;
      } else if (considerSingleLink &&
        (o.source === selectedNode['root'] && o.target === d ||
          o.source === d && o.target === selectedNode['root'])) {
        return o.edge_color;
      }
      return d3.rgb(238, 238, 238);
    });

  var placeholder = document.querySelector('#card-edge-placeholder');
  if (considerSingleLink) {
    // showLinkPopup(connectedLinks);
    showEdgeInformationInSidebar(placeholder);
  } else {
    placeholder.innerHTML = '';
  }
};


function styleFill(element, fill, opacity, transition) {
  element
    .transition(transition)
    .style('fill', fill)
    .style('opacity', opacity);
}

function styleStroke(element, stroke, opacity, transition) {
  element
    .transition(transition)
    .style('stroke', stroke)
    .style('opacity', opacity);
}


function showEdgeInformationInSidebar(placeholder) {
  placeholder.innerHTML = `
<head>
        <link rel="stylesheet" href="assets/css/sidebar.css">
</head>
<body>
<div id="edge-information-card">
	<div class="card-header" data-toggle="collapse" data-target="#edge-information-card-body"
		aria-expanded="true" aria-controls="edge-information-card-body">
		<p class="h7" id="edge-information-title">GENERAL INFORMATION</p>
		<hr>
	</div>

	<div id="edge-information-card-body" class="collapse show card-body">

	</div>
</div>
</body>
`;
  source = connectedLink.elementData.edges[0].source;
  target = connectedLink.elementData.edges[0].target;
  document.querySelector('#edge-information-title').innerText = `EDGES [${source}, ${target}]`;

  div = document.querySelector('#edge-information-card-body');
  edgeIndex = 1;

  connectedLink.elementData.edges.forEach(edge => {
    ul = document.createElement('ul');
    ul.setAttribute('id', `edge-information-${edgeIndex++}`);
    div.appendChild(ul);
    spanHeader = document.createElement('span');
    spanHeader.classList.add('first-header');
    spanHeader.innerText = `${edge.source} -> ${edge.target}`;
    ul.appendChild(spanHeader);

    appendNewLine(ul, 'predicted', edge.predicted);

    if (edge.predicted) {
      appendNewLine(ul, 'prediction score', edge.prediction_score);

      ulAm = document.createElement('ul');
      ulAm.setAttribute('id', `applied-methods`);
      div.appendChild(ulAm);

      for (let [method, methodList] of Object.entries(edge.applied_methods)) {
        spanHeader = document.createElement('span');
        spanHeader.classList.add('second-header');
        spanHeader.innerText = method;
        ulAm.appendChild(spanHeader);
        methodList.forEach(specMethod => {
          var specMethodsLi = document.createElement("li");
          ulAm.appendChild(specMethodsLi);
          var spanSpecMethod = document.createElement("span");
          spanSpecMethod.innerText = specMethod;
          specMethodsLi.appendChild(spanSpecMethod);
        });
      }


    }
  });
  var sidebar = document.querySelector('.sidebar');
  if (!sidebar.classList.contains('active')) {
    document.querySelector('#sidebarCollapse').click();
  }
}


function fillSidebarGeneralInformation(information) {
  var generalInfosNE = document.querySelector('#general-information-nodes-edges');
  generalInfosNE.querySelector('#general-information-node-count').textContent = information.node_count;
  generalInfosNE.querySelector('#general-information-directed-edges-count').textContent = information.directed_edge_count;
  generalInfosNE.querySelector('#general-information-undirected-edges-count').textContent = information.undirected_edge_count;

  var generalInfosMethods = document.querySelector('#general-information-methods');
  for (let [method, specMethods] of Object.entries(information.methods_applied)) {
    var spanHeader = document.createElement("span");
    spanHeader.classList.add('first-header');
    spanHeader.innerText = method;
    generalInfosMethods.appendChild(spanHeader);
    for (let [specMethod, count] of Object.entries(specMethods)) {
      appendNewLine(generalInfosMethods, specMethod, count);
    }

  }
}


function appendNewLine(parent, text1, text2) {
  var li = document.createElement("li");
  parent.appendChild(li);
  var span1 = document.createElement("span");
  span1.innerText = text1;
  li.appendChild(span1);
  var span2 = document.createElement("span");
  span2.innerText = text2;
  li.appendChild(span2);
}


function showLinkPopup(links) {
  $('.edgebar').toggleClass('active');

  var popoverInstance = undefined;
  if (links[0].rawElement._tippy !== undefined) {
    popoverInstance = links[0].rawElement._tippy;
  } else {
    popoverInstance = tippy(links[0].rawElement, {
      interactive: true,
      title: 'Hello, beauty',
      trigger: 'manual',
      updateDuration: 5,
      content: '<strong>Bolded content</strong><br><br><button class=\"hide\">Xfsdaf</button>',
      appendTo: document.body,
      onShown(popoverInstance) {
        var closeBtn = $('.hide').get(0);
        closeBtn.onclick = function () {
          popoverInstance.hide();
        };
        translationMatrix = network_group.node().transform.baseVal.consolidate().matrix;
        let distanceToLink = -(links[0].rawElement.getBBox().height * translationMatrix.d) / 2;
        popoverInstance.setProps({
          distance: distanceToLink
        });
      }
    });

  }
  popoverInstance.show(0);
}
