import { Injectable } from '@angular/core';
import { Predictor } from 'openapi_client';

@Injectable({
  providedIn: 'root'
})
export class ClassifierBuildService {
  private classifier: Predictor;
  private classifierConfigurated: boolean = false;

  constructor() { }

  getClassifier() {
    return this.classifier;
  }

  setClassifier(classifier: Predictor) {
    this.classifier = classifier;
  }

  setClassifierConfigurated(flag: boolean = false) {
    this.classifierConfigurated = flag;
  }

  buildClassifier() {
    this.classifier.parameters["isConfigurated"] = this.classifierConfigurated;

    let result = this.classifier;
    this.resetBuildService();

    return result;
  }

  resetBuildService() {
    this.classifier = undefined;
    this.classifierConfigurated = false;
  }
}
