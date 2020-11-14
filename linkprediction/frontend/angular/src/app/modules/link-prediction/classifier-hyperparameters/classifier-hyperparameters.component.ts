import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Predictor } from 'openapi_client';
import { ClassifierBuildService } from '../classifier-build.service';
import { PredictionSettingsService } from '../prediction-settings.service';

@Component({
  selector: 'app-classifier-hyperparameters',
  templateUrl: './classifier-hyperparameters.component.html',
  styleUrls: ['./classifier-hyperparameters.component.css']
})
export class ClassifierHyperparametersComponent implements OnInit {
  isLoaded: boolean = false;

  projectId: string;
  classifierId: string;
  selectedClassifier: Predictor;

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private predictionSettingsService: PredictionSettingsService,
    private classifierBuildService: ClassifierBuildService) { }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];
    this.selectedClassifier = this.classifierBuildService.getClassifier();

    this.isLoaded = true;
  }

  abortClassifierHyperparameterView() {
    this.classifierBuildService.resetBuildService();  
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

  saveSettings() {  
    let classifier = this.classifierBuildService.buildClassifier();
    this.predictionSettingsService.addPredictor(classifier);
    this.router.navigate(['project', this.projectId, 'prediction']);
    //this.router.navigate(['project', this.projectId, 'prediction', 'classifier', 'input']);
  }

}
