import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { PredictionService, Predictor } from 'openapi_client';
import { PredictorCategory } from '../predictorCategory';
import { Validators, FormControl, FormGroup } from '@angular/forms';
import { PredictionSettingsService } from '../prediction-settings.service';

@Component({
  selector: 'app-attribute-weightings',
  templateUrl: './attribute-weightings.component.html',
  styleUrls: ['./attribute-weightings.component.css']
})
export class AttributeWeightingsComponent implements OnInit {
  isLoaded: boolean = false;

  projectId: string;
  form: FormGroup;
  attribute_weightings: Array<any> = [];

  constructor(
    private router: Router,
    private dataRoute: ActivatedRoute,
    private predictionSettingsSerivce: PredictionSettingsService) { }

  ngOnInit() {
    this.projectId = this.dataRoute.snapshot.params['project_id'];

    this.attribute_weightings = this.predictionSettingsSerivce.getAttributeWeightings();
    this.form = this.toFormGroup(this.attribute_weightings);
    this.form.valueChanges.subscribe(() => {
      this.attribute_weightings.forEach(parameter => {
        parameter.value = this.form.value[parameter.attribute];
      })
    })

    this.isLoaded = true;
  }

  abortAttributeWeightingsView() {
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

  saveSettings() {
    this.predictionSettingsSerivce.setAttributeWeightings(this.attribute_weightings);
    this.router.navigate(['project', this.projectId, 'prediction']);
  }

  toFormGroup(parameters: any[] ) {
    let group: any = {};
    parameters.forEach(parameter => {
      group[parameter.attribute] = new FormControl(parameter.value || 1,
      Validators.required);
    });
    return new FormGroup(group);
  }

  isValid(name: string) { 
    return this.form.controls[name].valid; 
  }

}
