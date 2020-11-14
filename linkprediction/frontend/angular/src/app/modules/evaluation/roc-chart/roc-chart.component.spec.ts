import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RocChartComponent } from './roc-chart.component';

describe('RocChartComponent', () => {
  let component: RocChartComponent;
  let fixture: ComponentFixture<RocChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RocChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RocChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
