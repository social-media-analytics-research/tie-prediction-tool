import { Component, OnInit, Input } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'app-predictor-dynamic-form',
  templateUrl: './predictor-dynamic-form.component.html',
  styleUrls: ['./predictor-dynamic-form.component.css']
})
export class PredictorDynamicFormComponent implements OnInit {
  @Input() parameters: any[] = [];
  form: FormGroup;

  constructor() { }

  ngOnInit() {
    this.form = this.toFormGroup(this.parameters)
    this.form.valueChanges.subscribe(() => {
      this.parameters.forEach(parameter => {
        parameter.value = this.form.value[parameter.name];
      })
      this.onParametersChanged(this.parameters);
    })
    this.onParametersChanged(this.parameters);
  }

  toFormGroup(parameters: any[] ) {
    let group: any = {};
    parameters.forEach(parameter => {
      parameter.value = parameter.default;
      group[parameter.name] = new FormControl(parameter.value || '',
      Validators.required);
    });
    return new FormGroup(group);
  }

  onParametersChanged(parameters: Array<any>) {
    
  }
}
