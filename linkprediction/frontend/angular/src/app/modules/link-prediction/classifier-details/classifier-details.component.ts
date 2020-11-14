import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Predictor } from 'openapi_client';
import { PredictionSettingsService } from '../prediction-settings.service';

@Component({
  selector: 'app-classifier-details',
  templateUrl: './classifier-details.component.html',
  styleUrls: ['./classifier-details.component.css']
})
export class ClassifierDetailsComponent implements OnInit {
  isLoaded: boolean = false;

  projectId: string;

  selectedPredictorInputs: Array<Predictor> = [];

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private predictionSettingsService: PredictionSettingsService) { }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];

    let classifier = this.predictionSettingsService.getClassifierContext();
    this.selectedPredictorInputs = classifier.parameters["inputs"];
    this.isLoaded = true;
  }

  abortClassifierDetailsView() {
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

}
