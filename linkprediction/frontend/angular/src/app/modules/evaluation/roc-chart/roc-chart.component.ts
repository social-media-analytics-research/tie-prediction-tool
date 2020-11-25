import { Component, OnInit, Input, OnChanges } from '@angular/core';

import * as d3 from 'd3-selection';
import * as d3Scale from 'd3-scale';
import * as d3ScaleChromatic from 'd3-scale-chromatic';
import * as d3Shape from 'd3-shape';
import * as d3Array from 'd3-array';
import * as d3Axis from 'd3-axis';
import d3Tip from 'd3-tip';

declare const responsivefy: any;

@Component({
  selector: 'app-roc-chart',
  templateUrl: './roc-chart.component.html',
  styleUrls: ['./roc-chart.component.css']
})
export class RocChartComponent implements OnInit, OnChanges {
  @Input() data;
  roc_data_preprocessed = [];

  margin;
  width;
  height;
  svg;
  g;
  x;
  y;
  z;
  line;

  constructor() {
    this.margin = {top: 20, right: 70, bottom: 20, left: 70};
    this.width = 600 - this.margin.left - this.margin.right;
    this.height = 300 - this.margin.top - this.margin.bottom;
  }

  ngOnInit() {
    this.preprocessData();
    this.createChart();
  }

  ngOnChanges() {
    if(this.svg) {
      d3.select('#chart').select("svg").remove()
      this.ngOnInit();
    }
  }

  private createChart() {
    this.createChartDimensions();
    this.createXAxis();
    this.createYAxis();
    this.createZAxis();
    this.createLine();
    this.drawAxis();
    this.drawLines();
  }

  private createChartDimensions() {
    this.svg = d3.select('#chart')
      .append('svg')
        .attr('width', this.width + this.margin.left + this.margin.right)
        .attr('height', this.height + this.margin.top + this.margin.bottom)
        .call(responsivefy)

    this.g = this.svg
      .append('g')
        .attr('transform',
            'translate(' + this.margin.left + ',' + this.margin.top + ')');
  }

  private createXAxis() {
    this.x = d3Scale.scaleLinear()
      .domain([0, 1])
      .range([0, this.width]);
  }

  private createYAxis() {
    this.y = d3Scale.scaleLinear()
      .domain([0, 1])
      .range([this.height, 0]);
  }

  private createZAxis() {
    this.z = d3Scale.scaleOrdinal(d3ScaleChromatic.schemeCategory10);
  }

  private createLine() {
    this.line = d3Shape.line()
        .curve(d3Shape.curveBasis)
        .x( (d: any) => this.x(d['fpr']) )
        .y( (d: any) => this.y(d['tpr']) );
  }

  private preprocessData() {
    let roc_data = this.data;
    let roc_data_prepared = []
    Object.keys(roc_data).forEach(predictor => {
      let data = [];
      for(var counter:number = 0; counter<roc_data[predictor]['ROC']['tpr'].length; counter++){
        data.push({'tpr': roc_data[predictor]['ROC']['tpr'][counter], 'fpr': roc_data[predictor]['ROC']['fpr'][counter]})
      }
      roc_data_prepared.push({
        'id': predictor,
        'values': data
      });
    })
    this.roc_data_preprocessed = roc_data_prepared;
  }

  private drawAxis(): void {
    this.g.append('g')
        .attr('class', 'axis axis--x')
        .attr('transform', 'translate(0,' + this.height + ')')
        .call(d3Axis.axisBottom(this.x))
        .append('text')
        .attr('transform', 'rotate(0)')
        .attr('x', this.width - 6)
        .attr('y', -15)
        .attr('dy', '0.71em')
        .attr('fill', '#000')
        .text('FPR');

    this.g.append('g')
        .attr('class', 'axis axis--y')
        .call(d3Axis.axisLeft(this.y))
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '0.71em')
        .attr('fill', '#000')
        .text('TPR');
  }

  private drawLines(): void {
    let predictors = this.g.selectAll('.predictors')
        .data(this.roc_data_preprocessed)
        .enter().append('g')
        .attr('class', 'predictors');

    let tip = d3Tip()
      .attr('class', 'd3-tip')
      .style("visibility","visible")
      .offset([-20, 0])
      .html(function(d) {
        return `<strong>` + d.id + `</strong>`;
      });

    this.svg.call(tip)

    predictors.append('path')
        .attr('class', 'line')
        .attr('d', d => this.line(d.values) )
        .style('stroke', d => this.z(d.id) )
        .attr("fill", "none")
        .attr("stroke-width", 1.5)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .on("mouseover", function(d) { tip.show(d, this); })
        .on("mouseout", d => tip.hide(d));
  }

}
