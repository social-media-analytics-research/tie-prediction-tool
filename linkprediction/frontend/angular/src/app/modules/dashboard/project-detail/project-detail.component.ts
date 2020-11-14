import { Component, OnInit, Input } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProjectsService, NetworksService, PredictionService, PredictionState, PredictionStatus } from 'openapi_client';
import { PredictionSettingsService } from '../../link-prediction/prediction-settings.service';
import { PredictorParametersComponent } from '../../link-prediction/predictor-parameters/predictor-parameters.component';
import { PredictorCategory } from '../../link-prediction/predictorCategory';

@Component({
  selector: 'app-project-detail',
  templateUrl: './project-detail.component.html',
  styleUrls: ['./project-detail.component.css']
})
export class ProjectDetailComponent implements OnInit {
  isLoaded: boolean = false;
  isPredicting: boolean = false;
  projectId: string;

  projectName: string;
  projectDescription: string;
  graphName: string;
  node_count: string;
  edge_count: string;
  directed: string;
  multigraph: string;

  lastPrediction: string;
  machineLearning: boolean;
  highestAUC: string;

  predictionProgressMessage: string;
  predictionStepMessage: string;
  predictionMonitoringInterval; //NodeJS.Timer

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private projectsService: ProjectsService,
    private networksService: NetworksService,
    private predictionService: PredictionService,
    private predictionSettingsService: PredictionSettingsService) { }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];

    this.projectsService.getProjectById(this.projectId).subscribe(
      (result) => {
        this.projectName = result.designation;
        this.projectDescription = result.description;

        this.networksService.getOriginalNetworkByProject(this.projectId).subscribe(
          (result) => {
            this.graphName = String(result.designation);
            this.node_count = String(result.node_count);
            this.edge_count = String(result.edge_count);
            this.directed = String(result.directed);
            this.multigraph = String(result.multigraph);

            this.getEvaluationResults();
          },
          (error) => {
            console.log(error);
          }
        );
      },
      (error) => {
        console.log(error);
      }
    );
  }

  getEvaluationResults() {
    this.predictionService.getEvaluationResultsByProject(this.projectId).subscribe(
      (result) => {
        if(!('train_results' in result.results)) {
          this.lastPrediction = "-";
          this.highestAUC = "-";
        }
        else {
          this.lastPrediction = this.getLastPrediction(result);
          this.highestAUC = this.getHighestAccuracy(result);
        }

        this.machineLearning = this.getMachineLearningFlag();
        this.isLoaded = true;
      },
      (error) => {
        console.log(error);
      })
  }

  abortDetailView() {
    this.router.navigate(['/dashboard']);
  }

  configurePrediction() {
    this.router.navigate(['/project', this.projectId, 'prediction']);
  }

  startPrediction() {
    let predictionHandler: PredictionState = {
      "state": PredictionState.StateEnum.Start
    };

    this.predictionService.handlePredictionStateByProject(
      this.projectId,
      predictionHandler
    ).subscribe(
      (result) => {
        this.startPredictionMonitoring();
      },
      (error) => {
        console.log(error);
      }
    );
  }

  handlePredictionStatus(status: PredictionStatus) {
    switch(status.state) {
      case PredictionStatus.StateEnum.Finished: {
        if(status.current_step_name == 'Prediction') {
          this.handlePredictionFinished();
        }
        break;
      }
      case PredictionStatus.StateEnum.Failed: {
        this.handlePredictionFailed();
        break;
      }
      case PredictionStatus.StateEnum.Processing: {
        this.handlePredictionProcessing(status);
        break;
      }
      case PredictionStatus.StateEnum.Waiting: {
        this.handlePredictionWaiting();
        break;
      }
      default: {
        this.stopPredictionMonitoring();
        break;
      }
    }
  }

  handlePredictionFinished() {
    this.predictionStepMessage = 'Prediction successfully!';
    this.stopPredictionMonitoring();
    this.getEvaluationResults();
  }

  handlePredictionFailed() {
    this.predictionStepMessage = 'Prediction failed or aborted!';
    this.stopPredictionMonitoring();
  }

  handlePredictionProcessing(status: PredictionStatus) {
    this.predictionProgressMessage = this.buildPredictionProgressMessage(status);
    this.predictionStepMessage = this.buildPredictionStepMessage(status);
  }
  
  handlePredictionWaiting() {
    this.predictionStepMessage = 'Setup prediction process...'
  }


  buildPredictionProgressMessage(status: PredictionStatus) {
    return `Step ${status['current_step']}  of  ${status['max_steps']}`
  }

  buildPredictionStepMessage(status: PredictionStatus) {
    return `${status['current_step_name']}`;
  }

  startPredictionMonitoring(interval: number = 100) {
    this.predictionMonitoringInterval = setInterval(() => {
      this.getPredictionStatus();
    }, interval);

    this.isPredicting = true;
  }

  stopPredictionMonitoring() {
    if(this.predictionMonitoringInterval) {
      clearInterval(this.predictionMonitoringInterval);
    }
    this.isPredicting = false;
  }

  getPredictionStatus() {
    this.predictionService.getPredictionStatusByProject(this.projectId).subscribe(
      (result) => {
        this.handlePredictionStatus(result);
      },
      (error) => {
        console.log(error);
        this.stopPredictionMonitoring();
      }
    );
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

  getMachineLearningFlag() {
    let predictors = this.predictionSettingsService.getSelectedPredictors();
    return predictors.some(predictor => predictor.category == PredictorCategory.ML_classifier);
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

  canStartPrediction() {
    let predictors = this.predictionSettingsService.getSelectedPredictors();
    if(predictors.length > 0) {
      return predictors.some(predictor => predictor.category != PredictorCategory.ML_classifier);
    }
    return false;
  }
}
