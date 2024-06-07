import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-export',
  templateUrl: './export.component.html',
  styleUrls: ['./export.component.css']
})
export class ExportComponent implements OnInit {

  constructor(private router: Router) {}

  ngOnInit(): void {
    window.location.href = 'http://localhost:8000/export';
  }
}
