import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';
import { Router } from '@angular/router';
import { ProjectsService, Project } from 'openapi_client';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  isLoaded: boolean = false;

  projects: Array<Project>;

  constructor(
    private router: Router, 
    private projectsService: ProjectsService) { }

  ngOnInit() {
    this.refreshDashboard(null);
  }

  createProject() {
    this.router.navigate(['/project']);
  }

  refreshDashboard(event) {
    this.projectsService.getProjects().subscribe(
      (result) => {
        this.projects = result;
        this.isLoaded = true;
      },
      (error) => {
        console.log(error);
        this.projects = [];
      }
    );
  }
}
