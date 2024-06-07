import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-pokemons',
  templateUrl: './pokemons.component.html',
  styleUrls: ['./pokemons.component.css']
})
export class PokemonsComponent implements OnInit {

  constructor(private router: Router) {}

  ngOnInit(): void {
    window.location.href = 'http://localhost:8000/pokemons?start_index=0&page_size=50';
  }



}
