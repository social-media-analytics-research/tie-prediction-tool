import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'app-predictor-parameters',
  templateUrl: './predictor-parameters.component.html',
  styleUrls: ['./predictor-parameters.component.css']
})
export class PredictorParametersComponent {
  @Input() parameter: any;
  @Input() form: FormGroup;

  get isValid() { 
    return this.form.controls[this.parameter.name].valid; 
  }

  parseCategoryToJSON(category: any) {
    return JSON.parse(category);
  }
}
