import { Injectable } from '@angular/core';
import { PredictionService, Predictor, PredictionSetup, EvaluationSetup } from 'openapi_client';
import { PredictorCategory } from './predictorCategory';

@Injectable({
  providedIn: 'root'
})
export class PredictionSettingsService {
  private projectId: string;
  private availablePredictors: Array<Predictor> = [];
  private selectedPredictors: Array<Predictor> = [];
  private attribute_weightings: Array<any>;

  private ensembleContext: Predictor;
  private classifierContext: Predictor;

  private evaluationSetup: EvaluationSetup;

  constructor(
    private predictionService: PredictionService) { }

  initializePredictorsByProject(projectId: string) {
    this.projectId = projectId;
    this.predictionService.getPredictorsByProject(this.projectId).subscribe(
      (result) => {
        this.availablePredictors = result.available_predictors;
        this.selectedPredictors = result.selected_predictors;
        this.attribute_weightings = this.searchForAttributeWeightings();
      },
      (error) => {
        console.log(error);
      }
    );

    this.predictionService.getEvaluationResultsByProject(this.projectId).subscribe(
      (result) => {
        let evaluation_setup: EvaluationSetup = {
          "random_seed": 42,
          "with_validation": result.results['with_validation'],
          "train_sampling_ratio": result.results['train_sampling_ratio'],
          "test_sampling_ratio": result.results['test_sampling_ratio'],
          "ml_preprocessing": result.results['ml_preprocessing']
        }
        this.evaluationSetup = evaluation_setup;
      },
      (error) => {
        console.log(error)
      }
    );
  }

  getAvailablePredictors() {
    return this.availablePredictors;
  }


  getSelectedPredictors() {
    return this.selectedPredictors;
  }


  getEvaluationSetup() {
    return this.evaluationSetup;
  }

  setEvaluationSetup(newEvaluationSetup: EvaluationSetup) {
    this.evaluationSetup = newEvaluationSetup;
  }

  addPredictor(newPredictor: Predictor) {
    this.selectedPredictors.push(newPredictor);
  }

  deletePredictor(predictorToDelete: Predictor) {
    const index: number = this.selectedPredictors.indexOf(predictorToDelete);
    if (index !== -1) {
      this.selectedPredictors.splice(index, 1);
    }
  }

  savePredictors() {
    this.populateWithAttributeWeightings(this.selectedPredictors);

    let predictionSetup: PredictionSetup = {
      selected_predictors: this.selectedPredictors,
      evaluation_setup: this.evaluationSetup 
    }

    this.predictionService.deletePredictionSetup(this.projectId).subscribe(
      (result) => {
        this.predictionService.createPredictionSetup(
          this.projectId,
          predictionSetup
          ).subscribe(
            (result) => {
              this.predictionService.getPredictorsByProject(this.projectId).subscribe(
                (result) => {
                  this.availablePredictors = result.available_predictors;
                  this.selectedPredictors = result.selected_predictors;
                  this.attribute_weightings = this.searchForAttributeWeightings();
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
      },
      (error) => {
        console.log(error)
      }
    )
  }

  getClassifierContext() {
    return this.classifierContext;
  }

  setClassifierContext(classifier: Predictor) {
    this.classifierContext = classifier;
  }

  getEnsembleContext() {
    return this.ensembleContext;
  }

  setEnsembleContext(ensemble: Predictor) {
    this.ensembleContext = ensemble;
  }

  getAttributeWeightings() {
    return this.attribute_weightings;
  }

  setAttributeWeightings(attribute_weightings: Array<any>) {
    this.attribute_weightings = attribute_weightings;
  }

  private searchForAttributeWeightings() {
    let socialTheoryExogenous = this.getSocialTheoryExogenous(this.selectedPredictors)[0];

    if(socialTheoryExogenous == undefined) {
      socialTheoryExogenous = this.getSocialTheoryExogenous(this.availablePredictors)[0]; 
    }

    return socialTheoryExogenous.parameters['attribute_weightings'];
  }

  private getSocialTheoryExogenous(predictors: Array<Predictor>) {
    return predictors.filter(predictor => 
      predictor.category == PredictorCategory.Social_theory_exogenous);
  }

  private populateWithAttributeWeightings(selectedPredictors: Array<Predictor>) {
    selectedPredictors.forEach(predictor => {
      if(predictor.category == PredictorCategory.Social_theory_exogenous) {
        predictor.parameters['attribute_weightings'] = this.attribute_weightings;
      }
    });
  }
}
