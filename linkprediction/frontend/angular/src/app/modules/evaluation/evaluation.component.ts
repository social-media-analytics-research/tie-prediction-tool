import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ProjectsService, NetworksService, PredictionService, Project, EvaluationResults } from 'openapi_client';
import { IDropdownSettings } from 'ng-multiselect-dropdown';
import { Router } from '@angular/router';
import { PredictionSettingsService } from '../link-prediction/prediction-settings.service';

@Component({
  selector: 'app-evaluation',
  templateUrl: './evaluation.component.html',
  styleUrls: ['./evaluation.component.css']
})
export class EvaluationComponent implements OnInit {
  isLoaded: boolean = false;
  isError: boolean = false;
  projectsAvailable: boolean = false;
  evaluationAvailable: boolean = false;
  errorMessage: string = '';
  projects: Array<Project> = [];
  selectedProject: Project;

  validation: boolean;
  ml_preprocessing: boolean;
  train_ratio: number;
  test_ratio: number;
  train_results;
  test_results;
  
  roc_data
  auc_data;
  displayed_roc_data;
  displayed_auc_data;
  display_validation;

  dropdown_settings: IDropdownSettings = {};
  dropdown_list = [];
  selected_predictors = [];

  constructor(
    private router: Router,
    private projectsService: ProjectsService,
    private networksService: NetworksService,
    private predictionService: PredictionService,
    private predictionSettingsService: PredictionSettingsService) { }

  ngOnInit() {
    this.dropdown_settings = {
      singleSelection: false,
      idField: 'item_id',
      textField: 'item_text',
      selectAllText: 'Select All',
      unSelectAllText: 'UnSelect All',
      itemsShowLimit: 3,
      allowSearchFilter: false
    };

    this.display_validation = false;

    this.projectsService.getProjects().subscribe(
      (result) => {
        this.projects = result;

        if(this.projects && this.projects.length > 0) {
          this.selectedProject = this.projects[0];
          this.projectsAvailable = true;
        }
        else {
          this.isLoaded = true;
          return
        }

        this.getEvaluationByProject();
      },
      (error) => {
        console.log(error);
        this.isError = true;
        this.errorMessage = 'Something went wrong...'
        this.projects = []
        this.isLoaded = true;
      }
    );
  }

  prepareAucData(results) {
    let auc_scores = []
    let predictors = Object.keys(results);
    predictors.forEach(predictor => {
      auc_scores.push({"predictor": predictor, 
                       "auc_score": Number(results[predictor]['AUC']).toFixed(2)});
    })

    // Sort descending
    auc_scores.sort((a,b) => 0 - (a['auc_score'] > b['auc_score'] ? 1 : -1));
    return auc_scores;
  }

  createDropdownList(results) {
    let id_counter = 0;
    let selection = [];
    let predictors = Object.keys(results);
    predictors.forEach(predictor => {
      selection.push({item_id: id_counter, item_text: predictor});
      id_counter += 1;
    });
    return selection;
  }

  updateView() {
    this.displayed_roc_data = {}
    for(let key in this.roc_data) {
      if(this.selected_predictors.some(function(predictor) {
        return predictor['item_text'] == key;
      })) {
        this.displayed_roc_data[key] = this.roc_data[key];
      }
    }

    this.displayed_auc_data = this.auc_data.filter(score => {
      return this.selected_predictors.some(function(predictor) {
        return predictor['item_text'] == score['predictor'];
      })
    })
  }

  displayTrainResults() {
    this.display_validation = false;
    this.roc_data = this.train_results;
    this.auc_data = this.prepareAucData(this.train_results);
    this.updateView();
  }

  displayTestResults() {
    this.display_validation = true;
    this.roc_data = this.test_results;
    this.auc_data = this.prepareAucData(this.test_results);
    this.updateView();
  }

  getEvaluationByProject() {
    this.predictionService.getEvaluationResultsByProject(this.selectedProject.id).subscribe(
      (result) => {
        this.display_validation = false;
        this.evaluationAvailable = false;
        if(!('train_results' in result.results)) {
          this.isLoaded = true;
          return
        }

        this.validation = result.results['with_validation'];
        this.ml_preprocessing = result.results['ml_preprocessing'];
        this.train_ratio = result.results['train_sampling_ratio'];
        this.test_ratio = result.results['test_sampling_ratio'];
        this.train_results = result.results['train_results'];
        this.test_results = result.results['test_results']

        this.roc_data = this.train_results;
        this.auc_data = this.prepareAucData(this.train_results);
        
        this.dropdown_list = this.createDropdownList(this.train_results);
        this.selected_predictors = [this.dropdown_list[0]];
        this.updateView()
        this.evaluationAvailable = true;
        this.isLoaded = true;
      },
      (error) => {
        console.log(error)
        this.isError = true;
        this.errorMessage = 'Something went wrong...'
        this.isLoaded = true;
      }
    )
  }

  selectedProjectChanged() {
    this.getEvaluationByProject();
  }

  createPrediction() {
    this.predictionSettingsService.initializePredictorsByProject(this.selectedProject.id);
    this.router.navigate(['/project', this.selectedProject.id]);
  }

  createProject() {
    this.router.navigate(['/project']);
  }
}
