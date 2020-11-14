import {Component, OnInit} from '@angular/core';
import {Router, ActivatedRoute} from '@angular/router';
import {Predictor, EvaluationSetup} from 'openapi_client';
import {PredictionSettingsService} from './prediction-settings.service';
import {ClassifierBuildService} from './classifier-build.service';

@Component({
  selector: 'app-link-prediction',
  templateUrl: './link-prediction.component.html',
  styleUrls: ['./link-prediction.component.css']
})
export class LinkPredictionComponent implements OnInit {
  isLoaded: boolean = false;

  projectId: string;
  selectedPredictors: Array<Predictor> = [];
  availableClassifiers: Array<Predictor> = [];
  selectedClassifier;
  defaultClassifierFlag: boolean = true;
  evaluationSetup: EvaluationSetup;

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private predictionSettingsService: PredictionSettingsService,
    private classifierBuildService: ClassifierBuildService) {
  }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];
    this.selectedPredictors = this.predictionSettingsService.getSelectedPredictors();
    this.availableClassifiers = this.getAvailableClassifiers(
      this.predictionSettingsService.getAvailablePredictors()
    );
    this.selectedClassifier = this.availableClassifiers[0];
    this.evaluationSetup = this.predictionSettingsService.getEvaluationSetup();
    this.isLoaded = true;
  }

  getAvailableClassifiers(availableFeatures: Array<Predictor>) {
    const classifiers = availableFeatures.filter(feature => feature.category == 'ML-Classifier');
    return classifiers;
  }

  viewPredictor(predictor: Predictor) {
    if (predictor.category == 'ML-Classifier') {
      this.predictionSettingsService.setClassifierContext(predictor);
      this.router.navigate(['project', this.projectId, 'prediction', 'classifier', 'detail']);
    } else if (predictor.category == 'Social-Theory-Ensemble') {
      this.predictionSettingsService.setEnsembleContext(predictor);
      this.router.navigate(['project', this.projectId, 'prediction', 'ensemble', 'detail']);
    }
  }

  deletePredictor(featureToDelete: Predictor) {
    this.predictionSettingsService.deletePredictor(featureToDelete);
  }

  addPredictor() {
    this.router.navigate(['project', this.projectId, 'prediction', 'predictor', 'add']);
  }

  createClassifier() {
    this.classifierBuildService.setClassifier(this.selectedClassifier);
    this.configureClassifier();
  }

  configureClassifier() {
    if (this.defaultClassifierFlag) {
      this.classifierBuildService.setClassifierConfigurated(false);
      let classifier = this.classifierBuildService.buildClassifier();
      this.predictionSettingsService.addPredictor(classifier);
      this.router.navigate(['project', this.projectId, 'prediction']);
    } else {
      this.classifierBuildService.setClassifierConfigurated(true);
      this.router.navigate(['project', this.projectId, 'prediction', 'classifier', 'hyperparameters']);
    }
  }

  configureAttributeWeightings() {
    this.router.navigate(['project', this.projectId, 'prediction', 'attribute_weightings']);
  }

  abortPredictionSettingsView() {
    this.predictionSettingsService.initializePredictorsByProject(this.projectId);
    this.router.navigate(['/project', this.projectId]);
  }

  saveSettings() {
    this.predictionSettingsService.setEvaluationSetup(this.evaluationSetup);
    this.predictionSettingsService.savePredictors();
    this.router.navigate(['/project', this.projectId]);
  }

  onValidationActivate() {
    this.evaluationSetup.with_validation = !this.evaluationSetup.with_validation;
  }

  parametersAvailable(predictor: Predictor) {
    if (this.parametersAvailableFlag(predictor)) {
      return "Available";
    } else {
      return "Unavailable";
    }
  }

  parametersAvailableFlag(predictor: Predictor) {
    if (Object.keys(predictor.parameters).length === 0) {
      return false;
    } else {
      return true;
    }
  }

  toPercentage(value) {
    return Math.trunc(value * 100);
  }
}
