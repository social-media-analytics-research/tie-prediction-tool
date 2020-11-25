import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { Project, ProjectsService, PredictionService } from 'openapi_client';
import { PredictionSettingsService } from '../../link-prediction/prediction-settings.service';

@Component({
  selector: 'app-project-tile',
  templateUrl: './project-tile.component.html',
  styleUrls: ['./project-tile.component.css']
})
export class ProjectTileComponent implements OnInit {
  @Output() refresh = new EventEmitter();
  @Input() project: Project;
  isLoaded: boolean = false;

  lastPrediction: string;
  highestAUC: string;

  constructor(
    private router: Router,
    private projectsService: ProjectsService, 
    private predictionService: PredictionService,
    private predictionSettingsService: PredictionSettingsService) { }

  ngOnInit() {
    this.predictionService.getEvaluationResultsByProject(this.project.id).subscribe(
      (result) => {
        if(!('train_results' in result.results)) {
          this.lastPrediction = "-";
          this.highestAUC = "-";
        }
        else {
          this.lastPrediction = this.getLastPrediction(result);
          this.highestAUC = this.getHighestAccuracy(result);
        }

        this.isLoaded = true;
      },
      (error) => {
        console.log(error);
      })
  }

  viewProject() {
    this.predictionSettingsService.initializePredictorsByProject(this.project.id);
    this.router.navigate(['/project', this.project.id])
  }

  editProject() {
    //Note: Backend implementation not available
    //this.router.navigate(['/project', this.project.id, 'edit'])
  }

  deleteProject() {
    if(confirm("Are you sure to delete " + this.project.designation + "?")) {
      this.projectsService.deleteProjectById(this.project.id).subscribe(
        (result) => {
          this.refresh.emit(null);
        },
        (error) => {
          console.log(error);
        }
      );
    }
  }

  getLastPrediction(result) {
    if(result.timestamp) {
      let date = new Date(0);
      date.setUTCSeconds(result.timestamp);
      let day = date.getDate();
      let month = date.getMonth();
      let year = date.getFullYear();
      let hh = date.getHours();
      let mm = date.getMinutes();
      return day + '.' + (month+1) + '.' + year + ' ' + (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
    }
    return '-';
  }

  getHighestAccuracy(result) {
    if('train_results' in result.results) {
      let auc_scores = []
      if(result.results['with_validation'] && result.results['test_results']) {
        let test_results = result.results['test_results'];
        let predictors = Object.keys(test_results);
        predictors.forEach(predictor => {
          auc_scores.push(Number(test_results[predictor]['AUC']).toFixed(2));
        });
        return String(Math.max(...auc_scores)  * 100) + ' %';
      }
      let train_results = result.results['train_results'];
      let predictors = Object.keys(train_results);
      predictors.forEach(predictor => {
        auc_scores.push(Number(train_results[predictor]['AUC']).toFixed(2));
      })
      return String(Math.max(...auc_scores)  * 100) + ' %';
    }
    return '-';
  }
}
