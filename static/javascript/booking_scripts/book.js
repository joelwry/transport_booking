document.addEventListener('DOMContentLoaded', function () {
    const vehicleId = VEHICLE_ID; // This is gotten from the variable  passed down from the views down to the book.html  
    const scheduleContainer = document.getElementById('schedule-container');
    let schedules = [] // for storing vehicle schedules
    // this will be used to recieve the user booked seats 
    let SELECTED_SEATS = [] // USER BOOKED SEATS

    async function fetchSchedules() {
        try {
            const response = await fetch(`/api/vehicle-schedules/?vehicle_id=${vehicleId}`);
            schedules = await response.json();
            filterSchedules()
            //renderSchedules(schedules);
        } catch (error) {
            console.error('Error fetching schedules:', error);
        }
    }

    function resetSelectedSeatsVariables(){
        // Reset the selected seats
        SELECTED_SEATS = [];
        document.getElementById('one-way-selected_seats').value = '';
        document.getElementById('round-trip-selected_seats').value = '';
    }

    function handleRadioClick(schedule) {
        const tripType = document.querySelector('input[name="trip-type"]:checked').value;
        const seatsContainer = document.getElementById(`${tripType}-seats`);
        
        document.getElementById(`${tripType}-selected-schedule`).innerHTML = `Book Seat for Trip from <span style='color: brown; font-weight: 600;'>${schedule.pickup_state_name}</span> to <span style='color: brown; font-weight: 600;'>${schedule.destination_state_name}</span>`;
        
        seatsContainer.innerHTML = ''; // Clear previous seats

        for (let i = 1; i <= schedule.vehicle_capacity; i++) {
            const seatDiv = document.createElement('div');
            seatDiv.classList.add('seat', 'col-3');
            seatDiv.dataset.seat = i;
            seatDiv.innerText = i;

            if (!schedule.available_seats.includes(i)) {
                seatDiv.classList.add('booked');
            }

            seatsContainer.appendChild(seatDiv);
        }
        resetSelectedSeatsVariables();
    }

    function filterSchedules() {
        const tripType = document.querySelector('input[name="trip-type"]:checked').value;
        let pickupState;
        let destinationState;
        if(tripType == 'one-way'){
            pickupState = document.querySelector('#one-way-form select[name="pickup_state"]').value;
            destinationState = document.querySelector('#one-way-form select[name="destination_state"]').value;
        }else{
            pickupState = document.querySelector('#round-trip-form select[name="pickup_state"]').value;
            destinationState = document.querySelector('#round-trip-form select[name="destination_state"]').value;
        }
        
        const filteredSched = schedules.filter(schedule => {
            return schedule.pickup_state === parseInt(pickupState) && schedule.destination_state === parseInt(destinationState);
        });
        renderSchedules(filteredSched);
    } 

    function limitSeatSelection() {
        const adultInput = document.querySelector('input[name="adults"]');
        const childInput = document.querySelector('input[name="children"]');
        const totalSeats = document.querySelector('.total-seats');

        adultInput.addEventListener('change', updateSeatLimits);
        childInput.addEventListener('change', updateSeatLimits);

        function updateSeatLimits() {
            const adults = parseInt(adultInput.value);
            const children = parseInt(childInput.value);
            const totalPassengers = adults + Math.ceil(children / 2);

            const tripType = document.querySelector('input[name="trip-type"]:checked').value;
            const selectedSeatsInput = document.getElementById(`${tripType}-selected_seats`);
            const maxSeats = parseInt(totalSeats.dataset.maxSeats);

            if (totalPassengers > maxSeats) {
                showToast('Total passengers exceed vehicle capacity!');
                return;
            }

            if (SELECTED_SEATS.length > totalPassengers) {
                showToast('Selected seats exceed total passengers!');
                return;
            }

            totalSeats.innerText = `Total Seats Selected: ${SELECTED_SEATS.length}/${totalPassengers}`;
        }
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 3000);
    }

    
    function renderSchedules(schedules) {
        scheduleContainer.innerHTML = '';
        schedules.forEach(schedule => {
            const card = document.createElement('div');
            card.className = 'col-md-4';
            card.innerHTML = `
                    <div class="card" style='box-shadow: 1px 1px 5px rgba(12, 12, 1, 0.1); border: 2px solid #d7f1febf; border-radius: 10px;  margin-bottom: 1rem;'>
                        <div class="card-body" style=' display: flex;justify-content: space-between;align-items: flex-start;flex-direction: column;'>
                            <div class="card-info">
                                <div class="route">${schedule.pickup_state_name} &rarr; ${schedule.destination_state_name}</div>
                                <div class="company" align="center">${schedule.vehicle_company}</div>
                                <div class="times">
                                    ${new Date(schedule.travel_datetime).toLocaleString()}
                                    <br>
                                    Capacity : ${schedule.vehicle_capacity}
                                    <br>
                                    Available : ${schedule.available_seats.length}
                                </div>
                            </div>
                            <div class="price">
                                <div class="cost" style="color: darkgreen; font-family: monospace;">${new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' }).format(schedule.vehicle_price)}</div>
                            </div>
                
                        </div>
                        <div class="custom-radio-wrapper">
                            <input type="radio" class="custom-radio" id="schedule-${schedule.id}" name="schedule" value="${schedule.id}">
                            <label for="schedule-${schedule.id}">Select</label>
                        </div>
                        
                    </div>
                `;
                card.querySelector('.custom-radio').addEventListener('change', () => handleRadioClick(schedule));
            scheduleContainer.appendChild(card);
        });
    }

    // function to allow click and selection of seats 
    function seatSelectionAndUnselection() {
        document.querySelectorAll('.seats-container').forEach(seatsDiv => {
            seatsDiv.addEventListener('click', function (event) {
                const tripType = document.querySelector('input[name="trip-type"]:checked').value;
                const selectedSeatsInput = document.getElementById(`${tripType}-selected_seats`);

                const target = event.target;
                if (target.classList.contains('seat') && !target.classList.contains('booked')) {
                    const seatNumber = Number(target.getAttribute('data-seat'));
                    if (target.classList.contains('selected')) {
                        target.classList.remove('selected');
                        SELECTED_SEATS = SELECTED_SEATS.filter(seat => seat !== seatNumber);
                    } else {
                        target.classList.add('selected');
                        SELECTED_SEATS.push(seatNumber);
                    }
                    selectedSeatsInput.value = SELECTED_SEATS.join(',');
                    console.log(`BOOKED SEATS: ${SELECTED_SEATS}`);
                }
            });
        });
    }
    document.querySelectorAll('input[name="trip-type"]').forEach(tripRadioElement =>{
        tripRadioElement.addEventListener("change",evt =>{
            resetSelectedSeatsVariables();
            document.querySelectorAll(".seats-container.row").forEach(seatContainer => seatContainer.innerHTML="");
            document.querySelector("input.custom-radio:checked").checked = false;
        })
    })
    //document.querySelector('form.user-form').addEventListener('submit', bookSeat);
    document.querySelectorAll('select[name="pickup_state"], select[name="destination_state"]').forEach(select => {
        select.addEventListener('change', evt =>{
            filterSchedules();
            resetSelectedSeatsVariables();
            document.querySelectorAll(".seats-container.row").forEach(seatContainer => seatContainer.innerHTML="");
        });
    });

    async function bookSeat(event) {
        event.preventDefault();
        const tripType = document.querySelector('input[name="trip-type"]:checked').value;
        console.log(event.target);

        let scheduleId;
        try{
            scheduleId = document.querySelector('.custom-radio-wrapper input[name="schedule"]:checked').value;
        }catch(error){
            return alert("You have to select a vehicle schedule to book ");
        }

        if(SELECTED_SEATS.length < 1){
            return alert('You haven"t booked a seat');
        }
        const adults = parseInt(document.querySelector('input[name="adults"]').value);
        const children = parseInt(document.querySelector('input[name="children"]').value);
        let actual_children_count = children;
        if(children == 2){
            actual_children_count = 1;
        }else if(children == 1){
            actual_children_count = 0;
        }

        if ( adults + actual_children_count > SELECTED_SEATS.length){
            return alert("Passenger boarding this vehicle is more than the seats booked\nNote 1 Child below 10 years of age can be lapped by guardina, while 2 children below 10 years of age equals 1 seat .. any other above 2 will have to book complete seat");
        }
        let trip;
        if( tripType == "one-way" ){
            trip = "ONE WAY";
        }else{
            trip = "ROUND TRIP";
        }
        const data = {
            seats: SELECTED_SEATS,
            "number_of_adults": adults,
            "number_of_children_below_10": children,
            trip_type: trip
        };
        
        try {
            const response = await fetch(`/api/bookings/${scheduleId}/book_seat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                showToast('Booking successful!');
                alert('booking successfull')
                const data = await response.json()
                console.log(data);
            } else {
                showToast('Booking failed!');
                alert('failed booking your ')
                const data = await response.json()
                console.log(data);
            }
        } catch (error) {
            console.error('Error booking seat:', error);
            showToast('Error booking seat!');
            alert('error occurred')
        }
    }

    document.querySelector("#form1").addEventListener("submit",bookSeat);
    document.querySelector("#form2").addEventListener("submit",bookSeat);

    fetchSchedules();
    seatSelectionAndUnselection();
    limitSeatSelection();

});
