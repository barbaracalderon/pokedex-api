import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { PokemonsComponent } from './pokemons/pokemons.component';
import { DataComponent } from './data/data.component';
import { ExportComponent } from './export/export.component';
import { DocsComponent } from './docs/docs.component';


export const routes: Routes = [
    { path: 'home', component: HomeComponent },
    { path: 'pokemons', component: PokemonsComponent },
    { path: 'data', component: DataComponent },
    { path: 'export', component: ExportComponent },
    { path: 'swagger', component: DocsComponent },
    { path: '', component: HomeComponent },
];
