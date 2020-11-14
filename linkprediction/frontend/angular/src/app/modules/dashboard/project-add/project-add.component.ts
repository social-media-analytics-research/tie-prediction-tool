import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {ProjectSetup, ProjectsService} from 'openapi_client';
import {HttpErrorResponse} from '@angular/common/http';

@Component({
  selector: 'app-project-add',
  templateUrl: './project-add.component.html',
  styleUrls: ['./project-add.component.css']
})
export class ProjectAddComponent implements OnInit {
  projectName: string;
  projectDescription: string;
  graphName: string;

  alertFlag = false;
  errorMessage: string;

  fileFormatToggle = true;
  standardFileSelected = false;
  // validFileFormats: string = ".txt";

  standardFile: Blob;
  fileName: string;
  fileFormat: string;
  fileFormats: { [fileExtension: string]: string } = {
    gexf: 'GEXF',
    graphml: 'GraphML',
    gml: 'GML',
    csv: 'CSV'
  };
  additionalFile: Blob;
  additionalFileName: string;

  constructor(
    private router: Router,
    private projectsService: ProjectsService
  ) {
  }

  ngOnInit() {
    this.fileFormat = this.fileFormats.gexf;
  }

  createProject() {
    this.projectsService.createProject(
      this.projectName,
      this.projectDescription,
      this.graphName,
      true,
      true,
      this.standardFile,
      this.fileFormat as ProjectSetup.FileFormatEnum,
      this.additionalFile
    ).subscribe(
      (result) => {
        console.log(result);
        this.router.navigate(['/dashboard']);
      },
      (error: HttpErrorResponse) => {
        console.log(error);
        this.alertFlag = true;
        this.errorMessage = error.error.detail;
      }
    );
  }

  abortProjectCreation() {
    this.router.navigate(['/dashboard']);
  }

  standardFileForm() {
    this.fileFormatToggle = true;
  }

  loadStandardFile(event) {
    this.standardFile = event.files[0] as Blob;
    this.fileName = event.files[0].name;
    this.fileFormat = this.fileFormats[this.fileName.split('.').pop()];
    this.standardFileSelected = true;
  }

  loadAdditionalFile(event) {
    this.additionalFile = event.files[0] as Blob;
    this.additionalFileName = event.files[0].name;
  }

  closeAlert() {
    this.alertFlag = false;
  }

  getFileFormatValues() {
    return Object.values<string>(this.fileFormats);
  }
}
