import { Component, OnInit, Input } from '@angular/core';
import { PredictionService, PredictionState } from 'openapi_client';

@Component({
  selector: 'app-prediction-spinner',
  templateUrl: './prediction-spinner.component.html',
  styleUrls: ['./prediction-spinner.component.css']
})
export class PredictionSpinnerComponent implements OnInit {
  @Input() projectId: string;
  @Input() predictionProgressMessage: string;
  @Input() predictionStepMessage: string;

  constructor(
    private predictionService: PredictionService) { }

  ngOnInit() {
  }

  abortPrediction() {
    let predictionHandler: PredictionState = {
      "state": PredictionState.StateEnum.Abort
    };

    this.predictionService.handlePredictionStateByProject(
      this.projectId,
      predictionHandler
      ).subscribe(
        (result) => {

        },
        (error) => {
          console.log(error);
        }
      );
  }
}
