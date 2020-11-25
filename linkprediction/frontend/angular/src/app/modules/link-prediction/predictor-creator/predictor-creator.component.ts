import { Component, OnInit, ViewChild} from '@angular/core';
import { NgForm } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { PredictionService, Predictor } from 'openapi_client';
import { PredictionSettingsService } from '../prediction-settings.service';
import { PredictorCategory } from '../predictorCategory';


@Component({
  selector: 'app-predictor-creator',
  templateUrl: './predictor-creator.component.html',
  styleUrls: ['./predictor-creator.component.css']
})
export class PredictorCreatorComponent implements OnInit {
  @ViewChild('ImportForm') CreatorForm: NgForm;
  isLoaded: boolean = false;
  parametersFormActive = false;
  projectId: string;
  predictorCategories: Array<string>;

  // Selected Theory
  selectedCategoryKey: string;
  selectedPredictorCategory: PredictorCategory;
  selectedAvailablePredictors: Array<Predictor>;
  selectedPredictor: Predictor;

  // Available Theories
  availableTopologies: Array<Predictor> = [];
  availableSocialTheoriesEndogenous: Array<Predictor> = [];
  availableSocialTheoriesExogenous: Array<Predictor> = [];
  availableOthers: Array<Predictor> = [];

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private predictionService: PredictionService,
    private predictionSettingsService: PredictionSettingsService) { }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];

    this.predictorCategories = Object.keys(PredictorCategory);
    const index: number = this.predictorCategories.indexOf("ML_classifier");
    if (index !== -1) {
      this.predictorCategories.splice(index, 1);
    }

    this.predictionService.getPredictorsByProject(this.projectId).subscribe(
      (result) => {
        let selectedPredictors = this.predictionSettingsService.getSelectedPredictors();
        let availablePredictors = result.available_predictors;

        this.availableTopologies = this.getTopology(availablePredictors, selectedPredictors);
        this.availableSocialTheoriesEndogenous = this.getSocialTheoryEndogenous(availablePredictors, selectedPredictors);
        this.availableSocialTheoriesExogenous = this.getSocialTheoryExogenous(availablePredictors, selectedPredictors);
        this.availableOthers = this.getOthers(availablePredictors, selectedPredictors);

        this.selectedCategoryKey = "Topology";
        this.selectedPredictorCategory = PredictorCategory.Topology;
        this.onSelectedPredictorCategory();

        this.isLoaded = true;
      },
      (error) => {
        console.log(error);
      }
    );
  }

  getTopology(predictors: Array<Predictor>, selectedPredictors: Array<Predictor>) {
    return predictors.filter(predictor =>
      this.isTopology(predictor) &&
      !this.isAlreadySelected(predictor, selectedPredictors));
  }

  getSocialTheoryEndogenous(predictors: Array<Predictor>, selectedPredictors: Array<Predictor>) {
    return predictors.filter(predictor =>
      this.isSocialTheoryEndogenous(predictor) &&
      !this.isAlreadySelected(predictor, selectedPredictors));
  }

  getSocialTheoryExogenous(predictors: Array<Predictor>, selectedPredictors: Array<Predictor>) {
    return predictors.filter(predictor =>
      this.isSocialTheoryExogenous(predictor) &&
      !this.isAlreadySelected(predictor, selectedPredictors));
  }

  getOthers(predictors: Array<Predictor>, selectedPredictors: Array<Predictor>) {
    return predictors.filter(predictor =>
      this.isOthers(predictor) &&
      !this.isAlreadySelected(predictor, selectedPredictors));
  }

  isAlreadySelected(predictor: Predictor, selectedPredictors: Array<Predictor>) {
    let result = selectedPredictors.some((selectedPredictor) => selectedPredictor.designation == predictor.designation);
    return result;
  }

  isTopology(predictor: Predictor) {
    return predictor.category == PredictorCategory.Topology;
  }

  isSocialTheoryEndogenous(predictor: Predictor) {
    return predictor.category == PredictorCategory.Social_theory_endogenous;
  }

  isSocialTheoryExogenous(predictor: Predictor) {
    return predictor.category == PredictorCategory.Social_theory_exogenous;
  }

  isOthers(predictor: Predictor) {
    return predictor.category == PredictorCategory.Others;
  }

  abortPredictorCreation() {
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

  createPredictor() {
    this.predictionSettingsService.addPredictor(this.buildPredictor());
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

  buildPredictor() {
    return this.selectedPredictor;
  }


  handleParametersForm() {
    this.activateParametersForm();
  }

  activateParametersForm() {
    this.parametersFormActive = false;
    if(this.selectedPredictor.parameters["arguments"]) {
      this.parametersFormActive = true;
      return this.parametersFormActive;
    }
  }

  onSelectedPredictorCategory() {
    this.selectedPredictorCategory = PredictorCategory[this.selectedCategoryKey];
    switch(this.selectedPredictorCategory) {
      case PredictorCategory.Topology: {
         this.selectedAvailablePredictors = this.availableTopologies;
         this.selectedPredictor = this.availableTopologies[0];
         if(this.selectedPredictor == undefined) {
          this.parametersFormActive = false;
          break;
         }
         this.handleParametersForm();
         break;
      }
      case PredictorCategory.Social_theory_endogenous: {
         this.selectedAvailablePredictors = this.availableSocialTheoriesEndogenous;
         this.selectedPredictor = this.availableSocialTheoriesEndogenous[0];
         if(this.selectedPredictor == undefined) {
          this.parametersFormActive = false;
          break;
         }
         this.handleParametersForm();
         break;
      }
      case PredictorCategory.Social_theory_exogenous: {
        this.selectedAvailablePredictors = this.availableSocialTheoriesExogenous;
        this.selectedPredictor = this.availableSocialTheoriesExogenous[0];
        if(this.selectedPredictor == undefined) {
          this.parametersFormActive = false;
          break;
         }
        this.handleParametersForm();
        break;
      }
      case PredictorCategory.Others: {
        this.selectedAvailablePredictors = this.availableOthers;
        this.selectedPredictor = this.availableOthers[0];
        if(this.selectedPredictor == undefined) {
          this.parametersFormActive = false;
          break;
         }
        this.handleParametersForm();
        break;
      }
      default: {
        this.selectedAvailablePredictors = this.availableTopologies;
        this.selectedPredictor = this.availableTopologies[0];
        if(this.selectedPredictor == undefined) {
          this.parametersFormActive = false;
          break;
         }
        this.handleParametersForm();
         break;
      }
    }
  }

  parseCategory(value : string) {
    return PredictorCategory[value];
  }
}
