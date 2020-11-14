import {Component, OnInit} from '@angular/core';
import {NetworksService, Project, ProjectsService} from 'openapi_client';
import { Router } from '@angular/router';

declare const drawNetwork: any;
declare const initialize: any;
declare const removeNetwork: any;
declare const sidebarCollapseJS: any;

@Component({
  selector: 'app-graph-visualization',
  templateUrl: './graph-visualization.component.html',
  styleUrls: ['./graph-visualization.component.css']
})
export class GraphVisualizationComponent implements OnInit {
  isLoaded = false;
  projectsAvailable = false;
  projects: Array<Project>;
  selectedProject: Project;

  constructor(
    private router: Router,
    private projectsService: ProjectsService,
    private networksService: NetworksService) {
  }

  ngOnInit() {
    this.requestProjects();
  }

  requestProjects() {
    this.projectsService.getProjects().subscribe(
      (result) => {
        this.projects = result;

        if (this.projects && this.projects.length > 0) {
          this.selectedProject = this.projects[0];
          this.projectsAvailable = true;
          this.requestPredictedNetwork();
          this.isLoaded = true;
        } else {
          this.projectsAvailable = false;
          this.isLoaded = true;
        }
      });
  }

  updateNetwork() {
    this.isLoaded = false;
    removeNetwork();
    this.requestPredictedNetwork();
    this.isLoaded = true;
  }

  requestPredictedNetwork() {
    this.networksService.getPredictedNetworkByProject(this.selectedProject.id).subscribe(
      (result) => {
        initialize();
        drawNetwork(result);
      },
      (error) => {
        console.log(error);
      }
    );
  }

  sidebarCollapse() {
    sidebarCollapseJS();
  }

  createProject() {
    this.router.navigate(['/project']);
  }
}
