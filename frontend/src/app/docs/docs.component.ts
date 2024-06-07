import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-docs',
  templateUrl: './docs.component.html',
  styleUrls: ['./docs.component.css']
})
export class DocsComponent implements OnInit {

  constructor(private router: Router) {}

  ngOnInit(): void {
    window.location.href = 'http://localhost:8000/docs';
  }

}
