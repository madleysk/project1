document.addEventListener('DOMContentLoaded', function(){	
	// Function transforming rate number to stars
	function format_rating(rate){
			var rating= parseInt(rate);
			var rating_stars= document.createElement("span");
			for (let i=0;i<rating;i++){
				let checked_star= document.createElement("span");
				checked_star.setAttribute('class','fa fa-star checked');
				rating_stars.appendChild(checked_star);
				}
			if((rate%rating).toFixed(0) == 1){
				//append half star if decimal part >= 5
				let checked_star= document.createElement("span");
				checked_star.setAttribute('class','fa fa-star-half checked');
				rating_stars.appendChild(checked_star);
				// Append the unchecked stars left
				for (let i=rating+1;i<5;i++){
					let unchecked_star= document.createElement("span");
					unchecked_star.setAttribute('class','fa fa-star-o unchecked');
					rating_stars.appendChild(unchecked_star);
				}
				}
			else{ //Append unchecked stars
				for (let i=rating;i<5;i++){
					let unchecked_star= document.createElement("span");
					unchecked_star.setAttribute('class','fa fa-star-o unchecked');
					rating_stars.appendChild(unchecked_star);
				}
				}
			return rating_stars;
			}
		// formating rating td
		document.querySelectorAll(".rating").forEach(span =>{
				let rate = span.innerHTML;
				span.innerHTML='';
				span.appendChild(format_rating(rate));
			});
});
